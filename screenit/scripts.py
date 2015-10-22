from __future__ import print_function
import sys, argparse, selenium, contextlib, os, time

from selenium.webdriver import Remote as WebdriverRemote
from selenium.webdriver.support.ui import WebDriverWait

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

        def is_ready(driver):
            state = driver.execute_script('return document.readyState')
            return state == 'complete'

        # Selenium fails silently (or seems to) unless we check first.
        if not os.path.isdir(settings.output):
            raise Exception("not a directory: {}".format(settings.output))

        with contextlib.closing(remote) as driver:
            for task in self.get_tasks(settings):
                try:
                    output = self.find_output_name(settings.output, task, overwrite=False)

                    print("{0} {1}".format(output, task['url']))
                    driver.get(task['url'])

                    # Note that usin sleep seems to cause the connection to
                    # terminate somehow.
                    wait = WebDriverWait(driver, settings.wait_timeout)
                    wait.until(is_ready)

                    driver.save_screenshot(output)
                except:
                    # If we get a failure here the closing context seems to fail
                    # as well which maens we don't get to see the outcome.
                    import traceback
                    traceback.print_exc()
                    raise

    def get_tasks(self, settings):
        tasks = []

        for number, arg in enumerate(settings.url):
            if '://' in arg:
                tasks.append({'url': arg, 'name': self._url_to_path(arg)})
                continue

            for line in open(arg):
                if not line.strip():
                    continue

                if ' ' in line:
                    name, url = line.strip().split(' ', 1)
                else:
                    url = line.strip()
                    name = self._url_to_path(url)

                tasks.append({'url': url.strip(), 'name': name})

        return tasks

    def _url_to_path(self, url):
        """Cheap and cheerful but works for most things."""
        return os.path.basename(url)

    def find_output_name(self, base, task, overwrite):
        name = task['name']
        tries = 1

        full_path = os.path.join(base, name) + ".png"

        while os.path.exists(full_path) and not overwrite:
            if tries > 10:
                raise Exception("too many tries to find a unique name")

            uniqued = "{0}.{1}.png".format(name, tries)
            full_path = os.path.join(base, uniqued)

            tries += 1

        return full_path

    def get_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("url", nargs="+")
        parser.add_argument("-w", "--webdriver", required=True,
                            help="Location to hub or webdriver.")
        parser.add_argument("-o", "--output", default=os.getcwd(),
                            help="Output screenshots to this directory.  (Default pwd)")
        parser.add_argument( "--wait-timeout", default=10, type=int,
                            help="Time to wait until document is ready.")
        parser.add_argument("-c", "--capabilities", action="append", default=[],
                            help="Add a capability.  (Default pwd)")
        return parser

    def get_settings(self, parser):
        return parser.parse_args(self.argv[1:])

def screenit_main():
    """Entry point."""
    sys.exit(ScreenitCli(sys.argv).run())
