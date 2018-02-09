from collections import OrderedDict
import datetime


class Request(object):
    def __init__(self, request_data):
        self.parse(request_data)
        self.method, self.path, self.request_version = self.parse(request_data)

    @classmethod 
    def parse(cls, request_data):
       return request_data.splitlines()[0].rstrip(b'\r\n').split() 


class Response(object):
    def __init__(self, headers=None):
        self.ready = False
        self.headers = OrderedDict(headers or {}) 

    def start_response(self, status, response_headers, exc_info=None):
        # This is a WSGI-defined callback (Check PEP333 for details)
        server_headers = [('Date', httpdate(datetime.datetime.now())), ('Server', 'WSGIServer 0.2')]
        self.status = status
        self.headers = self.headers.update(response_headers)
        self.ready = True

    def serialize(body):
        if not self.ready:
            raise ValueError('Not ready. self.start_response() Must be called by a WSGI-compatible framework.')

        response = 'HTTP/1.1 {status}\r\n'.format(status=status)

        for header in self.headers:
            response += '{}: {}\r\n'.format(*header)
        response += '\r\n'
        response += ''.join(body)

        return response


class AppRunner(object):
    """
    In charge of running the app object of the given framework.
    """
    def __init__(self, application, client_connection, cfg=None):
        self.cfg = cfg or {}
        self.application = application
        self.connection = client_connection

    def handle_request(self):
        self.request_data = self.connection.recv(1024)
    
        logging.info('### REQUEST ###"\n')
        logging.info('\n'.join(self.request_data.splitlines()))

        req  = Request(self.request_data)
        self.environ = self.make_wsgi_environ(req.method, req.path, req.request_version)

        response = Response()

        logging.info('### Response ###\n')
        logging.info('\n'.join(response.splitlines()))

        result = self.application(environ, response.start_response)
        self.client_connection.sendall(response.serialize(result))

    def make_wsgi_environ(self, method, path, version):
        # These variables are listed on pep-0333
        # Order doesn't matter with these, 
        # so stating them in a regular dict for convenience.
        return {
            # CGI-defined variables
            'REQUEST_METHOD': method,
            'SCRIPT_NAME': '',
            'PATH_INFO': path,
            'QUERY_STRING': '',  # TODO
            'CONTENT_TYPE': '',  # Maybe empty, implement something more specific (TODO)
            'SERVER_NAME': self.cfg.get('Server Name'),
            'SERVER_PORT': str(self.cfg.get('Server Port')),
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

