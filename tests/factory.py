import os, socket
from six.moves import urllib
from mock import patch
from unittest import TestCase

from servequnit.http import QunitRequestHandler
from servequnit.factory import ServerFactory, js_server
from servequnit.server import TestServerThread, ServerSettings

class JsServerTestCase(TestCase):
    def test_server_lifecycle_is_managed(self):
        with js_server() as server:
            self.assertEqual(True, server.is_alive())
            urllib.request.urlopen(server.url).read()

        self.assertEqual(False, server.is_alive())

        with js_server.context() as server:
            self.assertEqual(True, server.is_alive())

        self.assertEqual(False, server.is_alive())

    def test_settings_passed_to_server(self):
        with js_server(port=1234) as server:
            self.assertEqual(1234, server.port)

        with js_server.context(port=1234) as server:
            self.assertEqual(1234, server.port)

    def test_works_as_decorator(self):
        @js_server.decorate()
        def function(server):
            self.assertEqual(True, server.is_alive())

        function()

        @js_server.decorate(port=1234)
        def function(server):
            self.assertEqual(1234, server.port)

        function()
