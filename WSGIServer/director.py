import logging
import os
import signal
import socket
import sys


default_cfg = {
    'SOCKET_COUNT': 1,
}


def _configured_socket():
    _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return _socket


class Director(object):
    REQUIRED_CFG_FIELDS = ['SERVER_ADDRESS', 'SOCKET_COUNT']

    def __init__(self, cfg=None):
        self.sockets = []
        self._workers = {}

        self.cfg = default_cfg
        self.cfg.update(cfg or {})

        self.initialize_sockets()
       
    def cfg_errors(self):
        errors = []
        for item in self.REQUIRED_CFG_FIELDS:
            if item not in self.cfg.keys():
                errors.append('Missing "{}".'.format(item))
        return errors

    def initialize_sockets(self):
        cfg_errors = self.cfg_errors()
        if cfg_errors:
            raise ValueError('Configuration errors:\n{}'.format('\n'.join(cfg_errors)))

        while len(self.sockets) < self.cfg['SOCKET_COUNT']:
            logging.info('Making new socket')
            _socket = _configured_socket()
            _socket.bind(self.cfg['SERVER_ADDRESS'])
            _socket.listen(1)
            self.sockets.append(_socket)

    def close_sockets(self):
        for _socket in self.sockets:
            _socket.close()

    def stop_workers(self):
        for worker in self._workers.values():
            worker.stop()
                     
    def hire(self, worker_cls):
        """
        Pass in a worker_cls that implementes BaseWorker
        """
        # Get parent PID before forking.
        # The parent PID can be passed to the workers and is 
        # useful for checking if the parent is still running.
        parent_pid = os.getpid()

        worker = worker_cls(self.cfg, parent_pid=parent_pid)

        pid = os.fork()
        if pid != 0:
                self._workers[pid] = worker
                return pid

        worker.start(self.sockets)
        sys.exit()

    def fire(self, worker_id, force=False):
        """
        :worker_id:  ID of worker to fire
        "force: False, wait until worker is done with any activities.
                True, stop worker immediately.
        """
        worker = self._workers.get(worker_id)

        if worker and worker.stop(force=force):
            os.kill(worker_id, signal.SIGINT if force else signal.SIGTERM)
            del self._workers[worker_id]

    @property
    def workers(self):
        return self._workers.values()        

    #def __del__(self):
    #    self.close_sockets()
    #    self.stop_workers()

