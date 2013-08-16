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

    def _get_content(self, request):
        writes = request.files[-1].writes
        data = writes.index("\r\n")
        return "".join(writes[data:])

    def test_runner_response_displays_html(self):
        request = self._make_request("/test/blah.js")
        self._make_handler(request)
        self.assertEqual("HTTP/1.0 200 OK\r\n", request.files[-1].writes[0])

        document = self._get_content(request)

        self.assertTrue('<html>' in document)
        self.assertTrue('</html>' in document)

        # TODO:
        #   test it links our actual test

    def test_runner_responds_404_on_missing_test(self):
        # no point displaying the runner if there's nothing to run
        raise "ni"

    def test_unit_test_response_from_filesytem(self):
        # server.test_root + name
        raise "ni"

    def test_default_test_used_for_root(self):
        # /test[/]?
        # setver.get_default_test() from cli somehow (idea is for a short cli
        # like servequnit pants.js
        raise "ni"

    def test_404_if_no_default_test(self):
        raise "ni"

    def test_static_libraries_inserted(self):
        # script tags
        # server.libraries => /static/<path> src
        # server.content => /read/<name> => read from given location
        raise "ni"

    def test_bound_content_served_from_arbitary_path(self):
        # content actually turns up
        # server.content => /read/<name> => read from given location
        # also test 404 of this url type
        raise "ni"

    def test_function_mapped_to_url(self):
        # to yield fake ajax
        raise "ni"
