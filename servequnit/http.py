import SimpleHTTPServer

class QunitRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    #def log_message(self, format, *args):
    #    import sys
    #    sys.stderr.write(format + str(args) + "\n")

    def _respond(self, content, status=200, content_type='text/html'):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(content)
