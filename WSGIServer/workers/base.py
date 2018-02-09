



class BaseWorker(object):


    def __init__(self, cfg=None):
        self.cfg = cfg or {}

    def start(self):
        pass

    def stop(self):
        pass
