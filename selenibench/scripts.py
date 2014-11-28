from __future__ import print_function
import sys, argparse, selenium, contextlib, os

from selenium.webdriver import Remote as WebdriverRemote

class SelenibenchCli(object):
    def __init__(self, argv):
        self.argv = argv

    def run(self):
        parser = self.get_parser()
        settings = self.get_settings(parser)

        remote = WebdriverRemote(command_executor=settings.webdriver,
                                 desired_capabilities=settings.capabilities)

        with contextlib.closing(remote) as driver:
            driver.get(settings.url)

        return 0

    def get_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("url", nargs="+")
        parser.add_argument("-w", "--webdriver", required=True,
                            help="Location to hub or webdriver.")
        parser.add_argument("-c", "--capabilities", action="append", default=[],
                            help="Add a capability.  (Default pwd)")
        return parser

    def get_settings(self, parser):
        settings =  parser.parse_args(self.argv[1:])

        capabilities = {'browserName': "firefox"}

        for capability in settings.capabilities:
            name, value = capability.split("=")
            capabilities[name.strip()] = value.strip()

        settings.capabilities = capabilities

        return settings

def selenibench_main():
    """Command-line entry point."""
    cli = SelenibenchCli(sys.argv)
    sys.exit(cli.run())
