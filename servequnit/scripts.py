"""
Runs an HTTP server which serves up qunit unit tests.
"""
import argparse, SocketServer, SimpleHTTPServer, sys, signal, logging
from servequnit.factory import ServerFactory

QUNIT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<link rel="stylesheet" href="{qunit_css}">
<script type="text/javascript" src="/node_modules/requirejs/require.js"></script>
<script type="text/javascript" src="{qunit_js}"></script>
<script type="text/javascript" src="{sinon_js}"></script>
</head>
<body>
    <div id="qunit"></div>
    <div id="qunit-fixture"></div>
    {script_tag}
</body>
</html>\n"""

class QunitGenerator(object):
    """Generates the main body of a qunit test."""
    def __init__(self):
        self._name = None

    def script(self, name):
        self._name = name
        return self

    def render(self):
        context = {
            'script_tag': '<script type="text/javascript" src="/js/test/{0}.js"></script>'.format(self._name),
            'title': "Qunit Test Case",
            'sinon_js': "/js/test/_runner/sinon-1.7.3.js",
            'qunit_css': "http://code.jquery.com/qunit/qunit-1.12.0.css",
            'qunit_js': "http://code.jquery.com/qunit/qunit-1.12.0.js",
        }
        return QUNIT_HTML.format(**context)

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
