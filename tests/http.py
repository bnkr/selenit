import os, contextlib
from tempfile import NamedTemporaryFile
from mock import patch, Mock
from unittest import TestCase
from six.moves import urllib

from servequnit.server import ReusableServer, HandlerSettings
from servequnit.http import QunitRequestHandler
from servequnit.factory import js_server

from ._util import MockSocket, dump_page

class QunitRequestHandlerTestCase(TestCase):
    def _make_request(self, url):
        """There really doesn't seem to be a way to create HTTP requests as
        strings..."""
        request = MockSocket()
        request.queue_recv("GET {url} HTTP/1.1".format(url=url))
        return request

    def _make_settings(self, test_root=None, read=None,
                       scripts=None, styles=None):
        # TODO:
        #   Use a real server settings object.  It's simple enough that there's
        #   really not need to mock it.
        server = Mock(spec=ReusableServer)
        settings = Mock(spec=HandlerSettings)
        test_root = test_root or "/tmp"
        settings.test_root.return_value = test_root
        settings.bound_content.return_value = read
        settings.scripts.return_value = scripts or []
        settings.styles.return_value = styles or []
        server.get_handler_settings.return_value = settings
        return server

    @contextlib.contextmanager
    def _in_dir(self, where):
        old = os.getcwd()
        os.chdir(where)
        try:
            yield
        finally:
            os.chdir(old)

    def _make_handler(self, request, server=None):
        client_address = ("localhost", 42)
        server = server or self._make_settings()
        handler = QunitRequestHandler(request, client_address, server=server)
        return handler

    def _get_content(self, request):
        """Needs care because py2 does each line in an individual write whereas
        py3 does not."""
        writes = request.files[-1].writes
        transmission = b"".join(writes)
        data = transmission.index(b'\r\n\r\n') + 4
        return transmission[data:].decode("utf-8")

    def test_handler_works_with_socket_server(self):
        """Damn it is hard to create a fake server... so we'd better just check
        it works with the real one."""
        with js_server(handler_factory=QunitRequestHandler) as server:
            dump_page(server.url, "/test/")

    def test_root_404_lists_prefixes(self):
        request = self._make_request("/asdasd")
        handler = self._make_handler(request)
        self.assertEqual(b"HTTP/1.0 404 Not Found\r\n", request.files[-1].writes[0])
        last_line = request.files[-1].writes[-1]
        paths = [path for (path, _) in handler.get_handlers()]
        message = "404: '/asdasd': prefix must be one of {0!r}\n".format(paths)
        self.assertEqual(message, last_line)

    def test_static_response_serves_from_pwd(self):
        basename = os.path.basename(__file__)
        request = self._make_request("/static/{0}".format(basename))

        with self._in_dir(os.path.dirname(__file__)):
            self._make_handler(request)

        self.assertEqual(b"HTTP/1.0 200 OK\r\n", request.files[-1].writes[0])

        class_definition = b"class self.__class__.__name__(TestCase)"
        output = request.files[-1].writes
        self.assertTrue(any((class_definition in line) for line in output))

    def test_static_respnds_404_when_file_missing(self):
        assert not os.path.exists("pants")

        request = self._make_request("/static/pants")
        self._make_handler(request)
        self.assertEqual(b"HTTP/1.0 404 Not Found\r\n", request.files[-1].writes[0])
        last_line = request.files[-1].writes[-1]

        message = "404: '/static/pants' (maps to '{0}'): does not exist\n"
        fs_name = os.path.join(os.getcwd(), "pants")
        self.assertEquals(message.format(fs_name), last_line)

    def test_runner_response_displays_html(self):
        with NamedTemporaryFile() as io:
            io.write(b"summat")
            io.flush()

            settings = self._make_settings(test_root=os.path.dirname(io.name))
            request = self._make_request("/test/{0}".format(os.path.basename(io.name)))
            self._make_handler(request, settings)
            self.assertEqual(b"HTTP/1.0 200 OK\r\n", request.files[-1].writes[0])

            document = self._get_content(request)

            self.assertTrue('<html' in document)
            self.assertTrue('src="/unit/{0}"'.format(os.path.basename(io.name))
                            in document)
            self.assertTrue('</html>' in document)

    def test_runner_handles_no_test(self):
        settings = self._make_settings(test_root=None)
        settings.get_handler_settings.return_value.test_root.return_value = None
        request = self._make_request("/test/test/data/passes.js")
        self._make_handler(request, settings)
        self.assertEqual(b"HTTP/1.0 404 Not Found\r\n", request.files[-1].writes[0])
        self.assertTrue("no test root" in request.files[-1].writes[-1])

    def test_runner_reponds_404_if_test_case_missing(self):
        request = self._make_request("/test/blah.js")
        settings = self._make_settings(test_root="/tmp/")
        self._make_handler(request, settings)
        self.assertEqual(b"HTTP/1.0 404 Not Found\r\n", request.files[-1].writes[0])

        message = "404: '/test/blah.js': test case '/unit/blah.js' (maps to " \
                  "'/tmp/blah.js'): does not exist\n"
        last_line = request.files[-1].writes[-1]
        self.assertEquals(message, last_line)

    def test_runner_inserts_libraries(self):
        request = self._make_request("/test/")
        settings = self._make_settings(scripts=["/static/a", '/blah/b'])
        self._make_handler(request, settings)

        document = self._get_content(request)
        self.assertTrue('src="/static/a"' in document)
        self.assertTrue('src="/blah/b"' in document)

    def test_runner_inserts_styles(self):
        request = self._make_request("/test/")
        settings = self._make_settings(styles=['/arbitrary_stuff/here'],)
        self._make_handler(request, settings)
        html = '<link rel="stylesheet" type="text/css" ' \
               'href="/arbitrary_stuff/here">'
        content = b"".join(request.files[-1].writes).decode("utf-8")
        self.assertTrue(html in content)

    def test_unit_test_js_responds_404_on_missing_test(self):
        request = self._make_request("/unit/blah.js")
        settings = self._make_settings(test_root="/tmp/")
        self._make_handler(request, settings)
        self.assertEqual(b"HTTP/1.0 404 Not Found\r\n", request.files[-1].writes[0])

        message = "404: '/unit/blah.js' (maps to '/tmp/blah.js'): does not exist\n"
        last_line = request.files[-1].writes[-1]
        self.assertEquals(message, last_line)

    def test_unit_test_response_from_filesytem(self):
        with NamedTemporaryFile() as io:
            file_content = b"some stuff\n"
            io.write(file_content)
            io.flush()

            request = self._make_request("/unit/" + os.path.basename(io.name))
            settings = self._make_settings(test_root=os.path.dirname(io.name))
            self._make_handler(request, settings)

            last_line = request.files[-1].writes[-1]
            self.assertEquals(file_content, last_line)

    def test_bound_content_served_from_arbitary_path(self):
        with NamedTemporaryFile() as io:
            file_data = b"some stuff\n"
            io.write(file_data)
            io.flush()

            request = self._make_request("/read/pants")
            settings = self._make_settings(read=[('pants', io.name)])
            self._make_handler(request, settings)

            last_line = request.files[-1].writes[-1]
            self.assertEquals(file_data, last_line)

    def test_bound_is_404_for_non_existing_path(self):
        request = self._make_request("/read/pants")
        settings = self._make_settings(read=[('pants', "/tmp.asdhasdas")])
        self._make_handler(request, settings)

        message = "404: '/read/pants' (maps to '/tmp.asdhasdas'): does not exist\n"
        last_line = request.files[-1].writes[-1]
        self.assertEquals(message, last_line)

    def test_bound_is_404_for_non_existing_name(self):
        request = self._make_request("/read/pants")
        settings = self._make_settings()
        self._make_handler(request, settings)

        message = "404: '/read/pants': no file bound for 'pants'\n"
        last_line = request.files[-1].writes[-1]
        self.assertEquals(message, last_line)
