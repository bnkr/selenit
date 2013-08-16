import urllib, os, contextlib
from mock import patch
from unittest import TestCase

from servequnit.http import QunitRequestHandler
from servequnit.factory import js_server

from ._util import MockSocket

class QunitRequestHandlerTestCase(TestCase):
    def test_handler_works_with_socket_server(self):
        """Damn it is hard to create a fake server... so we'd better just check
        it works with the real one."""
        with js_server(handler_factory=QunitRequestHandler) as server:
            urllib.urlopen(server.url).read()

    def _make_request(self, url):
        """There really doesn't seem to be a way to create HTTP requests as
        strings..."""
        request = MockSocket()
        request.queue_recv("GET {url} HTTP/1.1".format(url=url))
        return request

    @contextlib.contextmanager
    def _in_dir(self, where):
        old = os.getcwd()
        os.chdir(where)
        try:
            yield
        finally:
            os.chdir(old)

    def _make_handler(self, request):
        client_address = ("localhost", 42)
        handler = QunitRequestHandler(request, client_address, server=None)
        return handler

    def test_static_response_serves_from_pwd(self):
        basename = os.path.basename(__file__)
        request = self._make_request("/static/{0}".format(basename))

        with self._in_dir(os.path.dirname(__file__)):
            self._make_handler(request)

        self.assertEqual("HTTP/1.0 200 OK\r\n", request.files[-1].writes[0])

        class_definition = "class self.__class__.__name__(TestCase)"
        output = request.files[-1].writes
        self.assertTrue(any((class_definition in line) for line in output))

    def test_root_404_is_simple(self):
        request = self._make_request("/asdasd")
        self._make_handler(request)
        self.assertEqual("HTTP/1.0 404 Not Found\r\n", request.files[-1].writes[0])
        last_line = request.files[-1].writes[-1]
        self.assertEquals("404: urls must start /test/ or /static/\n", last_line)

    def test_static_404_is_simple(self):
        request = self._make_request("/static/pants")
        self._make_handler(request)
        self.assertEqual("HTTP/1.0 404 Not Found\r\n", request.files[-1].writes[0])
        last_line = request.files[-1].writes[-1]

        message = "404: '{0}' (from url '/static/pants')\n"
        message = message.format(os.path.join(os.getcwd(), "pants"))
        self.assertEquals(message, last_line)
