import threading, random, os, SocketServer, sys

from logging import getLogger

from servequnit.network import get_external_address, get_random_port
from servequnit.http import QunitRequestHandler

class ServerSettings(object):
    """DTO to initalise the server with."""
    def __init__(self, **kw):
        self._base_dir = None
        self._port = None
        self._host = None
        self._handler_factory = QunitRequestHandler

        # TODO: Not keen...
        for name, value in kw.iteritems():
            getattr(self, name)(value)

    def handler_factory(self, factory):
        self._handler_factory = factory
        return self

    def base_dir(self, value):
        assert os.path.isabs(value)
        self._base_dir = value
        return self

    def host(self, value):
        self._host = value
        return self

    def port(self, value):
        self._port = int(value)
        return self

class ReusableServer(SocketServer.TCPServer):
    """Messing about to get the port to be re-usable."""
    allow_reuse_address = True

    def shutdown(self):
        """Try really hard to avoid port still in use errors.  Note that the
        function calls must be in this order!"""
        self.socket.close()
        SocketServer.TCPServer.shutdown(self)

class TestServerThread(threading.Thread):
    """Stoppable server thread.  The purpose of this class is to synchronise the
    server and its parent thread (which could be a unit test or just a raw
    server).  The extra thread is therefore some overhead, but it's much easier
    than trying to get a mono-threaded server to terminate when you tell it to!
    """
    def __init__(self, settings):
        self.port = settings._port or get_random_port()
        self.host = settings._host or get_external_address()
        self.base_dir = settings._base_dir
        self.handler_factory = settings._handler_factory

        self._initialised = threading.Event()
        self._httpd = None
        self._error = None

        threading.Thread.__init__(self)

    @property
    def url(self):
        "Externally routable url to contact this server."
        return "http://{0}:{1}/".format(self.host, self.port)

    def run(self):
        "Sets up test server and loops over handling http requests."
        try:
            wtf = "server starting at {0} (from {1})"
            self._log(wtf.format(self.url, self.base_dir))
            if self.base_dir:
                os.chdir(self.base_dir)
            httpd = ReusableServer((self.host, self.port), self.handler_factory)
            self._httpd = httpd
        except Exception as ex:
            self._error = ex
            return
        finally:
            self._initialised.set()

        self._httpd.serve_forever()
        self._log("server thread terminating")

    def wait_for_start(self):
        "Start the thread and wait for the server to initialise without errors."
        self.start()
        self._initialised.wait()

        if self._error:
            self.join()
            raise self._error

        self._log("server has started on {0}.".format(self.url))

    def terminate_and_join(self, timeout=3):
        "Stop the thread and wait for it to finish."
        if not self._httpd:
            self._log("server not running")
            return

        self._log("waiting for server to terminate")
        try:
            # Very odd behaviour if this crashes.
            self._httpd.shutdown()
        finally:
            threading.Thread.join(self, timeout)

        self._log("collected server thread")

    def _log(self, message, *args, **kw):
        getLogger(__name__).info(message.format(*args, **kw))
