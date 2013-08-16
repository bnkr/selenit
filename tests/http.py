import urllib
from mock import patch
from unittest import TestCase

from servequnit.http import QunitRequestHandler
from servequnit.factory import js_server

class QunitRequestHandlerTestCase(TestCase):
    def test_handler_works_with_socket_server(self):
        """Damn it is hard to create a fake server... so we'd better just check
        it works with the real one."""
        with js_server(handler_factory=QunitRequestHandler) as server:
            response = urllib.urlopen(server.url).read()
            self.assertTrue("<html>" in response)

    def test_logging_uses_python(self):
        pass
