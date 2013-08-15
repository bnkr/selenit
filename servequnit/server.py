import threading, random, os, SocketServer, SimpleHTTPServer

from logging import getLogger

from servequnit.network import get_external_address, get_random_port

class QunitServer(SocketServer.TCPServer):
    """Handles requests dynamically to get qunit stuff."""

    # TODO:
    #   Do log handling better.

    def shutdown(self):
        """Try really hard to avoid port still in use errors."""
        SocketServer.TCPServer.shutdown(self)
        self.socket.close()

class ServerSettings(object):
    """DTO to initalise the server with."""
    def __init__(self):
        self._base_dir = None

    def base_dir(self, value):
        assert os.path.isabs(value)
        self._base_dir = value
        return self

class QunitServerThread(threading.Thread):
    """Stoppable server thread.  The purpose of this class is to synchronise the
    server and its parent thread (which could be a unit test or just a raw
    server).  The extra thread is therefore some overhead, but it's much easier
    than trying to get a mono-threaded server to terminate when you tell it to!
    """

    def __init__(self, settings):
        self.port = get_random_port()
        self.address = get_external_address()

        self._initialised = threading.Event()
        self._httpd = None
        self._error = None

        # might become irrelevant
        self.base_dir = settings._base_dir

        self.handler_factory = SimpleHTTPServer.SimpleHTTPRequestHandler

        threading.Thread.__init__(self)

    @property
    def url(self):
        "Externally routable url to contact this server."
        return "http://{0}:{1}/".format(self.address, self.port)

    def run(self):
        "Sets up test server and loops over handling http requests."
        try:
            wtf = "server starting at {0} (from {1})"
            self._log(wtf.format(self.url, self.base_dir))
            os.chdir(self.base_dir)
            bind = (self.address, self.port)
            httpd = QunitServer(bind, self.handler_factory)
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

    def terminate_and_join(self, timeout=None):
        "Stop the thread and wait for it to finish."
        # TODO: should be ok with server not running
        self._log("waiting for server to terminate")
        if self._httpd:
            try:
                # Very odd behaviour if this crashes.
                self._httpd.shutdown()
            finally:
                threading.Thread.join(self, timeout)
        self._log("collected server thread")

    def _log(self, message, *args, **kw):
        getLogger(__name__).info(message.format(*args, **kw))
