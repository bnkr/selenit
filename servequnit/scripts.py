"""
Runs an HTTP server which serves up qunit unit tests.
"""
import argparse, SocketServer, SimpleHTTPServer, sys, signal, logging
from servequnit.factory import ServerFactory

def get_settings(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", default=8081, help="Port to run on.",
                        type=int,)
    parser.add_argument("-H", "--host", default="localhost",
                        help="Host to listen on (default localhost).")

    settings = parser.parse_args(argv[1:])

    return settings

def configure_logging(settings):
    message_format = '%(asctime)s %(levelname)s %(name)s: %(message)s'
    time_format = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(level=logging.INFO, format=message_format,
                        datefmt=time_format)

def qunit_server():
    """Command-line entry point.  If your import paths are set right you can
    just call main() as the entire script."""
    settings = get_settings(sys.argv)
    configure_logging(settings)
    server = ServerFactory(port=settings.port, host=settings.host).create()
    try:
        # No need to thread; we just want the startup parts.
        server.run()
    except KeyboardInterrupt:
        # TODO:
        #   might need some cleanup if there are 500 errors -- that gets us the
        #   port already in use error sometimes.
        pass
    sys.exit(0)
