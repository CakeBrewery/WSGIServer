import logging
import os
import select

from WSGIServer.wsgi import AppRunner
from WSGIServer import util


class BaseWorker(object):
    def __init__(self, cfg=None):
        self.cfg = cfg or {}
        self.sockets = []

    def handle(self, client, addr):
        runner = AppRunner(self.cfg['app'], client)
        runner.handle_request()

    def clear_sockets(delete=True):
        for _socket in self.sockets:
            _socket.close()
        if delete:
            self.sockets = [] 

    @property
    def __worker_logger(self):
        # (Just an excuse to use currying)
        if hasattr(self, '__wl'):
            return self.__wl

        class WorkerLogger(object):
            pass
        self.__wl = WorkerLogger()
        def fn(method):
            def fn2(*args, **kwargs):
                rest_args = args[1:] if len(args) > 1 else []
                new_args = ['Worker {}: {}'.format(os.getpid(), args[0])] + rest_args
                return getattr(logging, method)(*new_args, **kwargs)
            return fn2

        for method in ['debug', 'info', 'warning', 'error', 'critical']:
            setattr(self.__wl, method, fn(method)) 
        return self.__wl

    @property
    def logging(self):
        return self.__worker_logger

    def start(self, sockets):
        for _socket in sockets:
            # Prevent leaking FDs
            util.close_on_exec(_socket)

        self.logging.info('Starting worker')
        if self.sockets:
            clear_sockets(delete=True)
        self.sockets = sockets if isinstance(sockets, list) else [socket]

        if not self.sockets:
            raise ValueError('Sockets must be provided')

        while True:
            try:
                if len(sockets) == 1:
                    self.logging.info('Waiting accept...')

                    client, addr = self.sockets[0].accept() 
                    util.close_on_exec(client)  # Let's make sure these FDs don't leak.

                    self.logging.info('HANDLING ONE')
                    self.handle(client, addr)
                    continue

                self.logging.info('SELECTING')
                socket_fds, _, _ = select.select(self.sockets, [], [])
                
                for _socket in socket_fds:
                    client, addr = _socket.accept()
                    util.close_on_exec(client)  # Let's make sure these FDs don't leak.

                    self.logging.info('HANDLING')
                    self.handle(client, addr)

            except EnvironmentError as e:
                if errno not in (errno.EAGAIN, errno.ECONNABORTED, errno.EWOULDBLOCK):
                    raise
     
    def stop(self):
        self.clear_sockets()

    #def __del__(self):
    #    self.stop()

