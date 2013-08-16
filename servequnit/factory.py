import contextlib, functools
from servequnit.server import TestServerThread, ServerSettings

class ServerFactory(ServerSettings):
    """Builder pattern to create the server and some utities to run it."""

    def create(self):
        return TestServerThread(self)

    @contextlib.contextmanager
    def run(self):
        server = self.create()
        try:
            server.wait_for_start()
            yield server
        finally:
            server.terminate_and_join()

class js_server(object):
    """Quickest possible api to get a test server running.  Can be used as a
    context manager or as a test decorator."""
    def __init__(self, **config):
        self.config = config
        self._server = None

    def __enter__(self):
        factory = ServerFactory(**self.config)
        self._server = factory.create()
        self._server.wait_for_start()
        return self._server

    def __exit__(self, ex_type, ex_value, ex_trace):
        if self._server:
            self._server.terminate_and_join()

    @classmethod
    def context(cls, **config):
        """For consistency with the decorate method."""
        with cls(**config) as server:
            function(server, *args, **kw)

    @classmethod
    def decorate(cls, **config):
        """Test method (or whatever) decorator."""
        def decorator(function):
            @functools.wraps(function)
            def run(*args, **kw):
                with cls(**config) as server:
                    function(server, *args, **kw)

            return run
        return decorator
