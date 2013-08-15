import urllib, os
from unittest import TestCase

from servequnit.server import QunitServerThread, ServerSettings

class QunitServerThreadTestCase(TestCase):
    def test_server_starts_thread(self):
        settings = ServerSettings().base_dir(os.path.realpath("."))
        server = QunitServerThread(settings)
        server.wait_for_start()
        self.assertTrue(server.is_alive())
        server.terminate_and_join()
        self.assertFalse(server.is_alive())
