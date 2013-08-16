import logging, os
from SimpleHTTPServer import SimpleHTTPRequestHandler

class QunitRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        """Url parsing, basically."""
        try:
            if self.path == "/shutdown/":
                self._respond("Server will shut down after this request.\n")
                # Causes an error later but does actually shut down.
                self.server.socket.close()
            elif self.path.startswith("/test/"):
                self._respond_test_main()
            elif self.path.startswith("/static/"):
                # data race but eh...
                without_static = self.path[len("/static"):]
                full_path = os.path.join(os.getcwd(), without_static[1:])
                if os.path.exists(full_path):
                    self.path = without_static
                    SimpleHTTPRequestHandler.do_GET(self)
                else:
                    missing = "{0!r} (from url {1!r})".format(full_path, self.path)
                    self._error(missing, status=404)
            else:
                self._error("urls must start /test/ or /static/", 404)
        except Exception as ex:
            # exceptions are printed in other weird ways... e.g. try raising
            # inside the log handler
            self._error("Exception.", status=500)
            raise

    def _error(self, message, status):
        why = "{0}: {1}\n".format(status, message)
        self._respond(why, status=status, content_type="text/plain")

    def _respond(self, content, status=200, content_type='text/html'):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(content)

    def log_error(self, format, status, description):
        """We're already sending all requests to the log so no need to do
        anything more for errors."""
        pass

    def log_message(self, format, *args):
        self._log("{0} {1} {2}", *args)

    def _log(self, message, *args, **kw):
        logging.getLogger(__name__).info(message.format(*args, **kw))

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
