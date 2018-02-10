from WSGIServer.wsgi import AppRunner
import select


class BaseWorker(object):
    def __init__(self, cfg=None):
        self.cfg = cfg or {}
        self.sockets = []

    def handle(self, sock, client, addr):
        runner = AppRunner(self.cfg['app'], client)
        runner.handle_request()

    def clear_sockets(delete=True):
        for _socket in self.sockets:
            _socket.close()
        if delete:
            self.sockets = [] 

    def start(self, sockets):
        print('Starting worker')
        if self.sockets:
            clear_sockets(delete=True)
        self.sockets = sockets if isinstance(sockets, list) else [socket]

        if not self.sockets:
            raise ValueError('Sockets must be provided')

        while True:
            try:
                print('SELECTING')
                socket_fds, _, _ = select.select(self.sockets, [], [], 1)
                
                for _socket in socket_fds:
                    client, addr = _socket.accept()
                    print('HANDLING')
                    self.handle(_socket, client, addr)

            except EnvironmentError as e:
                if errno not in (errno.EAGAIN, errno.ECONNABORTED, errno.EWOULDBLOCK):
                    raise
     
    def stop(self):
        self.clear_sockets()

    #def __del__(self):
    #    self.stop()

