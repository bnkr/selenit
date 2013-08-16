import logging
from SimpleHTTPServer import SimpleHTTPRequestHandler

class QunitRequestHandler(SimpleHTTPRequestHandler):
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
                SimpleHTTPRequestHandler.do_GET(self)
        except Exception as ex:
            # After a 500 and restart you get "address already in use".  Not
            # sure why but this is an attempt to stop that.
            self._respond("Error.", status=500, content_type="text/plain")
            raise

    def log_message(self, format, *args):
        request, status, something = args
        self._log("{0} {1} {2}", *args)

    def _log(self, message, *args, **kw):
        logging.getLogger(__name__).info(message.format(*args, **kw))

    def _respond(self, content, status=200, content_type='text/html'):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(content)
