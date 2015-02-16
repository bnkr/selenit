from __future__ import print_function
import sys, argparse, selenium, contextlib, os, json, traceback
from datetime import datetime as DateTime
from datetime import timedelta as TimeDelta

from selenium.webdriver import Remote as WebDriverRemote
from selenium.webdriver.support.ui import WebDriverWait

class SelenibenchCli(object):
    """Downloads timings from the web performance api."""

    def __init__(self, argv):
        self.argv = argv

    def run(self):
        parser = self.get_parser()
        settings = self.get_settings(parser)

        if settings.log_json:
            io = open(settings.log_json, 'w')
        else:
            io = None

        remote = WebDriverRemote(command_executor=settings.webdriver,
                                 desired_capabilities=settings.capabilities)

        runs = 0
        contiguous_failures = 0

        while runs < settings.number:
            runs += 1

            with contextlib.closing(remote) as driver:
                try:
                    driver.get(settings.url[0])
                    self.find_load_times(driver, io)
                    contiguous_failures = 0
                except:
                    if contiguous_failures > 3:
                        raise

                    contiguous_failures += 1
                    runs -= 1
                    traceback.print_ex()


        return 0

    def find_load_times(self, driver, log):
        def is_loaded(driver):
            return driver.execute_script("return (document.readyState == 'complete')")
        WebDriverWait(driver, 15).until(is_loaded)

        timings = driver.execute_script("return window.performance.timing")

        times = {}
        for key, value in timings.iteritems():
            if not isinstance(value, int):
                continue

            if value in (True, False):
                continue

            value = str(value)
            unixey = int(value[0:10])

            if value[10:]:
                ms = int(value[10:])
            else:
                ms = 0

            converted = DateTime.fromtimestamp(unixey)
            converted += TimeDelta(milliseconds=ms)

            times[key] = converted

        # This kind of thing really needs unit tests.  The thing takes so long
        # to run it's just going to break horribly.
        if log:
            serialisable = dict(
                    (key, value.isoformat())
                    for key, value in times.iteritems())
            log.write(json.dumps(serialisable))
            log.write("\n")

        print(times)

    def get_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("url", nargs="+")
        parser.add_argument("-w", "--webdriver", required=True,
                            help="Location to hub or webdriver.")
        parser.add_argument("-c", "--capabilities", action="append", default=[],
                            help="Add a capability.")
        parser.add_argument("-n", "--number", type=int, default=1,
                            help="How many requests to run.")
        parser.add_argument("-j", "--log-json", default=None,
                            help="Log json per-line for each hit.")
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
