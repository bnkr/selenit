import threading, random, os, sys, six

from six.moves import socketserver
from six.moves import urllib

from logging import getLogger

from servequnit.network import get_external_address, get_random_port
from servequnit.http import QunitRequestHandler

class SettingsError(Exception):
    pass

class ServerSettings(object):
    """DTO to initalise the server with.  Also decides the logic of defaults for
    different values."""
    def __init__(self, **kw):
        self._base_dir = None
        self._port = None
        self._host = None
        self._handler_factory = QunitRequestHandler
        self._bind = {}
        self._scripts = []
        self._styles = []

        # TODO: Not keen...
        for name, value in six.iteritems(kw):
            getattr(self, name)(value)

    def handler_factory(self, factory):
        self._handler_factory = factory
        return self

    def base_dir(self, value):
        assert os.path.isabs(value)
        self._base_dir = value
        return self

    def test_dir(self, value):
        assert os.path.isabs(value)
        self._test_dir = value
        return self

    def host(self, value):
        self._host = value
        return self

    def port(self, value):
        self._port = int(value)
        return self

    def script(self, url):
        """Put this script tag in each test."""
        self._scripts.append(url)
        return self

    def style(self, url):
        """Put this style tag in each test."""
        self._styles.append(url)
        return self

    def bind(self, name, path):
        """Bind a url to a filesystem path."""
        if not os.path.exists(path):
            why = "path in bind {0!r} does not exist: {1!r}"
            raise SettingsError(why.format(name, path))
        self._bind[name] = path
        return self

    def bind_script(self, name, path):
        """Shortcut."""
        self.bind(name, path)
        self.script(urllib.parse.urljoin("/read/", name))
        return self

    def bind_style(self, name, path):
        """Shortcut."""
        self.bind(name, path)
        self.style(urlparse.urljoin("/read/", name))
        return self

class HandlerSettings(object):
    """Mostly so we have a nice interface to pass to Mock."""

    # TODO:
    #   Not that useful as an abstraction.  We should just pass the
    #   serversettings object about.

    def __init__(self, settings):
        self.settings = settings

    def test_root(self):
        return self.settings._test_dir

    def bound_content(self):
        return list(six.iteritems(self.settings._bind))

    def styles(self):
        return self.settings._styles

    def scripts(self):
        return self.settings._scripts

class ReusableServer(socketserver.TCPServer):
    """Messing about to get the port to be re-usable."""
    allow_reuse_address = True

    #TODO: exceptions in request should go to logging

    def __init__(self, settings, bind, handler):
        """For some reason we can't wrap the request handler's constructor to
        pass settings so it has to get it from the server object."""
        # TODO:
        #    this might be a really trivial error... we should try again with
        #    the factory... having the hadnler settings here is needless
        #    coupling and would make it diffuclt for is to for example extract
        #    the server running stuff from the threading stuff
        socketserver.TCPServer.__init__(self, bind, handler)
        self.settings = settings

    def shutdown(self):
        """Try really hard to avoid port still in use errors.  Note that the
        function calls must be in this order!"""
        self.socket.close()
        socketserver.TCPServer.shutdown(self)

    def get_handler_settings(self):
        return self.settings

class TestServerThread(threading.Thread):
    """Stoppable server thread.  The purpose of this class is to synchronise the
    server and its parent thread (which could be a unit test or just a raw
    server).  The extra thread is therefore some overhead, but it's much easier
    than trying to get a mono-threaded server to terminate when you tell it to!
    """
    def __init__(self, settings):
        # TODO: this should all be done in the settings class
        self.handler_settings = HandlerSettings(settings)
        self.port = settings._port or get_random_port()
        self.host = settings._host or get_external_address()
        self.base_dir = settings._base_dir or os.getcwd()
        self.handler_factory = settings._handler_factory

        self._initialised = threading.Event()
        self._httpd = None
        self._error = None

        threading.Thread.__init__(self)

    @property
    def url(self):
        "Externally routable url to contact this server."
        return "http://{0}:{1}/".format(self.host, self.port)

    def run(self, sync_errors=True):
        """Sets up test server and loops over handling http requests.  Do not
        call this directly."""
        try:
            self._log("server starting at {0} in pwd {1}", self.url, self.base_dir)
            if self.base_dir:
                os.chdir(self.base_dir)
            httpd = ReusableServer(self.handler_settings,
                                   (self.host, self.port),
                                   self.handler_factory)
            self._httpd = httpd
        except Exception as ex:
            if sync_errors:
                self._error = (ex, None, sys.exc_info()[2])
                return
            else:
                raise
        finally:
            self._initialised.set()

        # TODO:
        #   Exception in here will be lost
        self._httpd.serve_forever()
        self._log("server thread terminating")

    def run_in_current_thread(self):
        """Disables special threading error handling so you still get an
        exception trace."""
        self.run(sync_errors=False)

    def wait_for_start(self):
        "Start the thread and wait for the server to initialise without errors."
        self.start()
        self._initialised.wait()

        if self._error:
            self.join()
            six.reraise(self._error[0], self._error[1], self._error[2])

        self._log("server has started on {0}.".format(self.url))

    def wait_for_stop(self, timeout=3):
        """Stop the thread and wait for it to finish."""
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

    def terminate_and_join(self, timeout=3):
        """Stop the thread and wait for it to finish."""
        return self.wait_for_stop(timeout=timeout)

    def _log(self, message, *args, **kw):
        getLogger(__name__).info(message.format(*args, **kw))
