



class BaseWorker(object):
    def __init__(self, cfg=None):
        self.cfg = cfg or {}
        self.sockets = []

    def handle(self, sock, client, addr):
        pass

    def handle_request(self, sock, req, client, addr):

    def start(self, sockets):
        self.sockets = sockets if isinstance(sockets, list) else [socket]

        while True:
            try:
                socket_fds = select.select(self.sockets, [], [], 1)
                
                for _socket in scoket_fds:
                    client, addr = _socket.accept()
                    self.handle(_socket, client, addr)

            except EnvironmentError as e:
                if errno not in (errno.EAGAIN, errno.ECONNABORTED, errno.EWOULDBLOCK):
                    raise
    
    def stop(self):
        for _socket in self.sockets:
            _socket.close()

    def __del__(self):
        self.stop()
        super(BaseWorker, self).__del__()
