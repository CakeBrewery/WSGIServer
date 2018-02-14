import time
import unittest
import logging
import psutil

from WSGIServer import director
from WSGIServer import workers
from WSGIServer import testapp


logging.getLogger().setLevel(logging.getLevelName('INFO'))


def find_all_child_processes(pids_only=False):
    """
    This might do. But apparently it's safer to log the
    pids of all child processes when creating them.
    "there isn't a posix compliant way to list child PIDS"
    - some guy on SO
    """
    children = psutil.Process().children(recursive=True)
    return [child.pid for child in children] if pids_only else children


class TestDirector(unittest.TestCase):

    def test_create_workers(self):

        test_director = director.Director({
            'SERVER_ADDRESS': ('localhost', 8888),
            'app': testapp.AppClass
        })

        pid1 = test_director.hire(workers.base.BaseWorker)
        pid2 = test_director.hire(workers.base.BaseWorker)
        self.assertEqual(len(find_all_child_processes()), 2)
        raise NotImplementedError(test_director.workers)

        while True:
            print('Waiting')
            time.sleep(60)


