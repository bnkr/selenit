from __future__ import print_function
import sys, argparse, selenium, contextlib, os

from selenium.webdriver import Remote as WebdriverRemote

class ScreenitCli(object):
    """Command-line runner for screenit."""
    def __init__(self, argv):
        self.argv = argv

    def run(self):
        parser = self.get_parser()
        settings = self.get_settings(parser)

        # There is a takesScreenshot capability.
        capabilities = {'browserName': "firefox"}

        for capability in settings.capabilities:
            name, value = capability.split("=")
            capabilities[name.strip()] = value.strip()

        remote = WebdriverRemote(command_executor=settings.webdriver,
                                 desired_capabilities=capabilities)

        with contextlib.closing(remote) as driver:
            for number, url in enumerate(settings.url):
                output = self.find_output_name(settings.output, number + 1, overwrite=False)
                driver.get(url)
                print("{0} {1}".format(output, url))
                driver.save_screenshot(output)

    def find_output_name(self, base, number, overwrite):
        name = "{0:03d}.png".format(number)
        if base:
            name = os.path.join(base, name)

        tries = 1
        while os.path.exists(name) and not overwrite:
            if tries > 10:
                raise Exception("too many tries")

            name = "{0:03d}.{1}.png".format(number, tries)
            if base:
                name = os.path.join(base, name)
            tries += 1

        return name

    def get_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("url", nargs="+")
        parser.add_argument("-w", "--webdriver", required=True,
                            help="Location to hub or webdriver.")
        parser.add_argument("-o", "--output",
                            help="Output screenshots to this directory.  (Default pwd)")
        parser.add_argument("-c", "--capabilities", action="append", default=[],
                            help="Add a capability.  (Default pwd)")
        return parser

    def get_settings(self, parser):
        return parser.parse_args(self.argv[1:])

def screenit_main():
    """Entry point."""
    sys.exit(ScreenitCli(sys.argv).run())
