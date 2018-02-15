import logging
import unittest
import WSGIServer

from WSGIServer import testapp


DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8888


class TestServer(unittest.TestCase):
    def test_server(self):
        server = WSGIServer.WSGIServer(('localhost', 8881), testapp.AppClass)
        logging.info('WSGI Server: Serving from {}:{}\n'.format(DEFAULT_HOST, DEFAULT_PORT))
        server.start()
