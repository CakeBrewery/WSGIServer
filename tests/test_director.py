import time
import unittest
import logging

from WSGIServer import director
from WSGIServer import workers
from WSGIServer import testapp


logging.getLogger().setLevel(logging.getLevelName('INFO'))


class TestDirector(unittest.TestCase):

    def test_create_workers(self):
        test_director = director.Director({
            'SERVER_ADDRESS': ('localhost', 8888),
            'app': testapp.AppClass
        })
        pid = test_director.hire(workers.base.BaseWorker)
        while True:
            print('Waiting')
            time.sleep(60)

        raise NotImplementedError(pid)

