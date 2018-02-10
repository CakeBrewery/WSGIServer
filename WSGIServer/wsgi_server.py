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

from exceptions import CannotKeepUp


logging.getLogger().setLevel(logging.getLevelName('INFO'))


DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8881

DEFAULT_CFG = {}

 
class WSGIServer(object):

    def __init__(self, server_address, application):
        self.cfg = DEFAULT_CFG.update({
            'SERVER_ADDRESS': server_address,
            'app': application
        })
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

