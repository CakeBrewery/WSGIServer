import logging
import unittest
import WSGIServer

from WSGIServer import testapp

from tests import simple_app


DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8888


class TestServer(unittest.TestCase):
    def test_server(self):
        server = WSGIServer.WSGIServer((DEFAULT_HOST, DEFAULT_PORT), testapp.AppClass)
        logging.info('WSGI Server: Serving from {}:{}\n'.format(DEFAULT_HOST, DEFAULT_PORT))
        server.start()


    def test_server_flask(self):
        server = WSGIServer.WSGIServer((DEFAULT_HOST, DEFAULT_PORT), simple_app.app)
        logging.info('WSGI Server: Serving from {}:{}\n'.format(DEFAULT_HOST, DEFAULT_PORT))
        server.start()

