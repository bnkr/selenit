"""
Runs an HTTP server which serves up qunit unit tests.
"""
import argparse, sys, logging, subprocess, os
from servequnit.tester import QunitSeleniumTester
from servequnit.factory import js_server, ServerFactory

class CliCommand(object):
    """Command pattern converts cli settings into an operation to run."""
    def __init__(self, settings):
        self.settings = settings

    def get_server_config(self):
        """Turn settings into parameters for factory'ing a server."""
        config = dict(
            port=self.settings.port,
            host=self.settings.host,
            test_dir=self.settings.root,
            base_dir=self.settings.doc_root,
        )
        return config

class SeleniumCommand(CliCommand):
    def get_tester_config(self, server):
        return dict(url=server.url + "default-case",
                    hub=self.settings.webdriver,)

    def run(self):
        try:
            server_config = self.get_server_config()
            with js_server.context(**server_config) as server:
                tester_config = self.get_tester_config(server)
                test = QunitSeleniumTester(**tester_config)
                test.run()
        except KeyboardInterrupt:
            pass

        return 0

class BrowserCommand(CliCommand):
    def run(self):
        try:
            server_config = self.get_server_config()
            with js_server.context(**server_config) as server:
                # could be a tester.BrowserTester?
                subprocess.call(['firefox', server.url + "default-case/"])
        except KeyboardInterrupt:
            pass

        return 0

class ServerCommand(CliCommand):
    def run(self):
        config = self.get_server_config()
        server = ServerFactory(**config).create()
        # No need to thread; we just want the startup parts.
        try:
            server.run()
        except KeyboardInterrupt:
            pass
        return 0

def get_settings(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", default=8081, help="Port to run on.",
                        type=int,)
    parser.add_argument("-H", "--host", default="localhost",
                        help="Host to listen on (default localhost).")
    parser.add_argument("-w", "--webdriver", default="http://127.0.0.1:4444/wd/hub",
                        help="Location of your webdriver HTTP endpoint.")
    parser.add_argument("-s", "--selenium", action="store_true", default=False,
                        help="Run tests with selenium and exit.")
    parser.add_argument("-b", "--browser", action="store_true", default=False,
                        help="Run tests with a web browser.")
    parser.add_argument("-r", "--root", default=os.getcwd(),
                        help="Root for test /unit files (js test files).")
    parser.add_argument("-d", "--doc-root", default=os.getcwd(),
                        help="Root for test /static files.")
    parser.add_argument("files", nargs="?",
                        help="Stuff to source in the test file (css or js).", )

    settings = parser.parse_args(argv[1:])

    return settings

def configure_logging(settings):
    message_format = '%(asctime)s %(levelname)s %(name)s: %(message)s'
    time_format = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(level=logging.INFO, format=message_format,
                        datefmt=time_format)

def servequnit_main():
    """Command-line entry point.  If your import paths are set right you can
    just call main() as the entire script."""
    settings = get_settings(sys.argv)
    configure_logging(settings)

    if settings.selenium:
        command = SeleniumCommand(settings)
    elif settings.browser:
        command = BrowserCommand(settings)
    else:
        command = ServerCommand(settings)

    sys.exit(command.run())
