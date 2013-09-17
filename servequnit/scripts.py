"""
Runs an HTTP server which serves up qunit unit tests.
"""
import argparse, sys, logging, subprocess, os, urlparse
from servequnit.tester import QunitSeleniumTester
from servequnit.factory import ServerFactory

class CliCommand(object):
    """Command pattern converts cli settings into an operation to run."""
    def __init__(self, settings):
        self.settings = settings

    def get_server_factory(self):
        """Turn settings into parameters for factory'ing a server."""
        config = dict(
            port=self.settings.port,
            host=self.settings.host,
            test_dir=self.settings.root,
            base_dir=os.getcwd(),
        )

        factory = ServerFactory(**config)

        # TODO:
        #   Present existence errors better.

        for name in (self.settings.files or []):
            if not name:
                continue

            if '=' in name:
                ident, location = name.split("=")
                if location.endswith(".css"):
                    factory.bind_style(ident, location)
                else:
                    factory.bind_script(ident, location)
            else:
                name = urlparse.urljoin("/static/", name)
                if name.endswith(".css"):
                    factory.style(name)
                else:
                    factory.script(name)

        return factory

class SeleniumCommand(CliCommand):
    def get_tester_config(self, server):
        return dict(url=server.url + "test",
                    hub=self.settings.webdriver,)

    def run(self):
        try:
            factory = self.get_server_factory()
            with factory.server_context() as server:
                tester_config = self.get_tester_config(server)
                test = QunitSeleniumTester(**tester_config)
                test.run()
        except KeyboardInterrupt:
            pass

        return 0

class BrowserCommand(CliCommand):
    def run(self):
        try:
            factory = self.get_server_factory()
            with factory.server_context() as server:
                # could be a tester.BrowserTester?
                subprocess.call([self.settings.browser, server.url + "test/"])
        except KeyboardInterrupt:
            pass

        return 0

class ServerCommand(CliCommand):
    def run(self):
        factory = self.get_server_factory()
        server = factory.create()
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
    parser.add_argument("-b", "--browser", default="unset", nargs="?",
                        help="Run tests with a web browser command.")
    parser.add_argument("-r", "--root", default=os.getcwd(),
                        help="Root for test /unit files (js test files). (default: pwd)")
    parser.add_argument("files", nargs="?", action="append",
                        help="Stuff to source in the test file (css or js).", )

    settings = parser.parse_args(argv[1:])

    if settings.browser == "unset":
        settings.browser = None
    elif settings.browser == None:
        settings.browser = "firefox"

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
