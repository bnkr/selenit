import urllib, os, socket
from mock import patch
from unittest import TestCase

from servequnit.server import TestServerThread, ServerSettings

class TestServerThreadTestCase(TestCase):
    def tearDown(self):
        """Nose blocks forever without this."""
        for server in getattr(self, '_servers', []):
            server.terminate_and_join()

    def _make_server(self, port=None):
        if not hasattr(self, '_servers'):
            self._servers = []

        settings = ServerSettings().base_dir(os.path.realpath("."))
        port and settings.port(port)
        server = TestServerThread(settings)
        self._servers.append(server)
        return server

    def test_server_starts_thread(self):
        settings = ServerSettings().base_dir(os.path.realpath("."))
        server = TestServerThread(settings)
        server.wait_for_start()
        self.assertTrue(server.is_alive())
        server.terminate_and_join()
        self.assertFalse(server.is_alive())

    @patch('servequnit.server.ReusableServer')
    def test_error_in_startup_stops_thread(self, http_class):
        class IdentifiableException(Exception):
            pass

        http_class.side_effect = IdentifiableException("pants")
        server = self._make_server()
        self.assertRaises(IdentifiableException, server.wait_for_start)
        self.assertFalse(server.is_alive())

    def test_terminate_stopped_server_is_noop(self):
        server = self._make_server()
        self.assertEqual(False, server.is_alive())
        server.terminate_and_join()
        self.assertEqual(False, server.is_alive())

    def test_reuse_thread_is_error(self):
        server = self._make_server()
        server.wait_for_start()
        server.terminate_and_join()
        self.assertRaises(RuntimeError, server.wait_for_start)

    def test_server_is_connectable_on_named_port(self):
        server = self._make_server(port=2234)
        server.wait_for_start()

        self.assertEqual(2234, server.port)
        self.assertTrue(":2234" in server.url)

        socket.create_connection((server.host, server.port), timeout=1)

        self.assertNotEqual("", urllib.urlopen(server.url).read())

    def test_reuse_port_is_ok(self):
        """Quite often you get 'port in use' after re-binding the same port
        which was recently used by the server."""
        server = self._make_server(port=4000)
        server.wait_for_start()
        self.assertTrue(server.is_alive())
        server.terminate_and_join()

        server = self._make_server(port=4000)
        server.wait_for_start()
        self.assertTrue(server.is_alive())
        server.terminate_and_join()
