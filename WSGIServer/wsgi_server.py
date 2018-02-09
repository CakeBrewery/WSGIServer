from __future__ import unicode_literals

import datetime
import errno
import logging
import os
from six import StringIO 
import socket
import sys

from workers.base import BaseWorker
from director import Director 

import handlers

from exceptions import (CannotKeepUp)

logging.getLogger().setLevel(logging.getLevelName('INFO'))


DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 8888


def httpdate(dt):
    """String representation in RFC 1123 """
    return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")


def _configured_socket():
    _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return _socket

   
class WSGIServer(object):

    def __init__(self, server_address, application):
        self.director = Director()
        self.socket = _configured_socket()

        self.socket.bind(server_address)
        self.socket.listen(1)

        host, port = self.socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port

        # As per the wsgi documentation. 
        # This is used as an object variable to store
        # state of the current processing request.
        # Check the examples on PEP 333
        self.headers_set = []

        self.application = application

    """
    def _fork_and_handle(self):
        # Simple half-assed implementation for supporting
        # multiple connections at the same time.
        pid = os.fork()
        
        # Upon fork, 0 is returned onto child process
        # pid of child is returned to parent process.
        if pid == 0:
            self.socket.close()  # Decrement socket file descriptor references
            self.handle_request()
            os._exit(0)
        else:
            self.client_connection.close()
    """
    
    def _next_connection(self):
        self.client_connection, client_address = self.socket.accept()
        return client_address

    def prefork(self):
        num_workers = 1 

        try:
            while len(self.direcotor.workers()) < num_workers:
                logging.info('Initializing worker. Total Workers: {}'.format(self.director.workers())
                director.hire(DefaultWorker):
        except CannotKeepUp as e:
            # While a bad thing, we can keep going. 
            logging.warning(e)

    def start(self):
        while True:
            self.prefork()

    def handle_request(self):
        self.request_data = self.client_connection.recv(1024)

        logging.info('### REQUEST ###:\n')
        logging.info('\n'.join(self.request_data.splitlines()))

        self.request_method, self.path, self.request_version = self.parse_request(self.request_data)
        environ = self.make_wsgi_environ(self.request_method, self.path, self.request_version)

        response = self.make_response(self.application(environ, self.start_response))

        logging.info('### RESPONSE ###\n')
        logging.info('\n'.join(response.splitlines()))

        self.client_connection.sendall(response)
        self.client_connection.close()
    
    def parse_request(self, data):
        return data.splitlines()[0].rstrip(b'\r\n').split()

    def make_wsgi_environ(self, method, path, version):
        # These variables are listed on pep-0333
        return {
            # CGI-defined variables
            'REQUEST_METHOD': method,
            'SCRIPT_NAME': '',
            'PATH_INFO': path,
            'QUERY_STRING': '',  # TODO
            'CONTENT_TYPE': '',  # Maybe empty, implement something more specific (TODO)
            'SERVER_NAME': self.server_name,
            'SERVER_PORT': str(self.server_port),
            'SERVER_PROTOCOL': 'HTTP/1.1', 
            'HTTP_VARIABLES': '',

            # WSGI-defined variables
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': (1, 0),
            'wsgi.input': StringIO(self.request_data.decode('utf-8')),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False
        }

    def start_response(self, status, response_headers, exc_info=None):
        # This is a wsgi-defined callback (check PEP 333 for more info)
        server_headers = [('Date', httpdate(datetime.datetime.now())), ('Server', 'WSGIServer 0.2')]
        self.headers_set = [status, response_headers + server_headers]

    def make_response(self, result):
        body = ''.join(chunk for chunk in result)
        
        status, response_headers = self.headers_set
        response = 'HTTP/1.1 {status}\r\n'.format(status=status)

        for header in response_headers:
            response += '{0}: {1}\r\n'.format(*header)
        response += '\r\n'
        response += ''.join(body)

        return response


if __name__ == '__main__':
    module, app_name = sys.argv[1].split(':')
    if not module:
        sys.exit('Please provide a python module with an app object.')

    module = __import__(module)

    if not app_name or not hasattr(module, app_name):
        sys.exit('Could not find application object "{}" in module {}.'.format(app_name, module))

    host, port = DEFAULT_HOST, DEFAULT_PORT  # Todo: Allow more options.

    application = getattr(module, app_name)

    handlers.initialize_handlers()

    server = WSGIServer((host, port), application)
    logging.info('WSGI Server: Serving from {}:{}\n'.format(host, port))
    server.start()

