import os
import signal


default_cfg = {
    'SOCKET_COUNT': 1 
}


def _configured_socket():
    _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return _socket


class Director(object):

    def __init__(self, cfg=None)
        self._workers = {}
        self.cfg = default_config.update(cfg)
        self.sockets = []
       
    def initialize_sockets(self):
        while len(sockets) < self.cfg.get['SOCKET_COUNT']:
            self.sockets.append(_configured_socket())

    def close_sockets(self):
        for _socket in self.sockets:
            _socket.close()
                     
    def hire(self, worker_cls):
        """
        Pass in a worker_cls that implementes BaseWorker
        """
        pid = os.fork()

        if pid != 0:
            worker = worker_cls(self.cfg)
            if worker and worker.id():
                self._workers[pid] = worker
                worker.start()
                return pid

    def fire(self, worker_id, force=False):
        """
        :worker_id:  ID of worker to fire
        "force: False, wait until worker is done with any activities.
                True, stop worker immediately.
        """
        worker = self._workers.get(worker_id)

        if worker and worker.stop(force=force):
            os.kill(pid, signal.SIGINT if force else signal.SIGTERM)
            del self._workers[worker_id]

    @attribute
    def workers():
        return self._workers.values()        

    def __del__(self):
        self.close_sockets()
        super(Director, self).__del__()
