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

from lexceptions import CannotKeepUp


logging.getLogger().setLevel(logging.getLevelName('INFO'))


DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8881

DEFAULT_CFG = {}


def httpdate(dt):
    """String representation in RFC 1123 """
    return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")


def _configured_socket():
    _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return _socket

   
class WSGIServer(object):

    def __init__(self, server_address, application):
        self.cfg = DEFAULT_CFG.update({'SERVER_ADDRESS': server_address})
        self.director = Director(self.cfg)
        self.application = application

    def prefork(self):
        num_workers = 1 

        try:
            while len(self.director.workers) < num_workers:
                logging.info('Initializing worker. Total Workers: {}'.format(self.director.workers))
                self.director.hire(BaseWorker)
        except CannotKeepUp as e:
            # While a bad thing, we can keep going. 
            logging.warning(e)

    def start(self):
        while True:
            self.prefork()


if __name__ == '__main__':
    module, app_name = sys.argv[1].split(':')
    if not module:
        sys.exit('Please provide a python module with an app object.')

    module = __import__(module)

    if not app_name or not hasattr(module, app_name):
        sys.exit('Could not find application object "{}" in module {}.'.format(app_name, module))

    application = getattr(module, app_name)

    handlers.initialize_handlers()

    server = WSGIServer(('localhost', 8881), application)
    logging.info('WSGI Server: Serving from {}:{}\n'.format(DEFAULT_HOST, DEFAULT_PORT))
    server.start()

