
"""
This is a test app to do first run of barebones WSGI server. 

This can be considered a VERY MINIMALISTIC framework that the
WSGI server ("gateway") should be able to support.
"""

# Test App as defined in PEP33
class AppClass:

    def __init__(self, environ, start_response):
        self.environ = environ
        self.start_response = start_response

    def __iter__(self):
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        self.start_response(status, response_headers)
        yield "Hello World!\n"

