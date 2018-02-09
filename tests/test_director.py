import unittest
from WSGIServer import director
from WSGIServer import workers


class TestDirector(unittest.TestCase):

    def test_create_workers(self):
        test_director = director.Director({'SERVER_ADDRESS': ('localhost', 8888)})
        pid = test_director.hire(workers.base.BaseWorker)

        raise NotImplementedError(pid)

