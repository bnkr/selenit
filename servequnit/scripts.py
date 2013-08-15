"""
Runs an HTTP server which serves up qunit unit tests.
"""
import argparse, SocketServer, SimpleHTTPServer, sys, signal

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

class QunitRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    # http://stackoverflow.com/questions/268629/how-to-stop-basehttpserver-serve-forever-in-a-basehttprequesthandler-subclass
    # http://stackoverflow.com/questions/1985197/using-simplehttpserver-for-unit-testing -- problems with address already in use

    def do_GET(self):
        """Url parsing, basically."""
        try:
            if self.path == "/shutdown/":
                self._respond("Server will shut down after this request.\n")
                # Even this doesn't seem to release the socket properly...
                self.server.shutdown()
            elif self.path.startswith("/test"):
                self._respond_test_main()
            else:
                super(QunitRequestHandler, self).do_GET()
        except Exception as ex:
            # After a 500 and restart you get "address already in use".  Not
            # sure why but this is an attempt to stop that.
            self._respond("Error.", status=500, content_type="text/plain")
            raise

    def _respond_test_main(self):
        """The qunit program."""
        name = self.path.split("/test", 2)[1]
        generator = QunitGenerator()
        self._respond(generator.script(name).render())

    def _respond(self, content, status=200, content_type='text/html'):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(content)

def get_server(settings):
    host, port = settings.host, settings.port
    return SocketServer.ThreadingTCPServer((host, port), QunitRequestHandler)

def get_settings(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", default=8081, help="Port to run on.",
                        type=int,)
    parser.add_argument("-H", "--host", default="localhost",
                        help="Host to listen on (default localhost).")

    settings = parser.parse_args(argv[1:])

    return settings

def handle_interrupt(server):
    def handler(signal, context):
        print "Terminating due to SIGINT."
        # TODO:
        #   do something with server to make it shutdown properly.  Solariffic
        #   has this kind of function somewhere.  Can't call server.shutdown as
        #   it deadlocks.  server.socket.close will work but it's a bit messy.
        #   Solariffic starts the server in a different thread and uses events
        #   to trigger the shutdown which is probably a bit cleaner.  We could
        #   also send a fake request (which would be nice anyway becuase you
        #   could shut it down over http).
        sys.exit(0)
    signal.signal(signal.SIGINT, handler)

def qunit_server():
    """Command-line entry point.  If your import paths are set right you can
    just call main() as the entire script."""
    settings = get_settings(sys.argv)
    httpd = get_server(settings)
    handle_interrupt(httpd)
    httpd.serve_forever()
    sys.exit(0)
