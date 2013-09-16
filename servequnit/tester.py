import logging
from selenium.webdriver import Remote
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait

class TestFailedError(Exception):
    pass

class QunitSeleniumTester(object):
    """Runs selenium tests against an arbitrary http location which serves a
    qunit test page."""

    QUNIT_RESULTS_ID = "qunit-testresult"
    FAILED_CLASS = "failed"
    TOTAL_CLASS = "total"

    def __init__(self, url, hub):
        self.url = url
        self.hub = hub
        self.capabilities = DesiredCapabilities.FIREFOX
        self.driver = None
        self.timeout = 10

    def _create_webdriver(self):
        self._log("connecting to selenium at {0}", self.hub)
        driver = Remote(command_executor=self.hub,
                        desired_capabilities=self.capabilities)
        self.driver = driver
        return driver

    def _log(self, message, *args, **kw):
        logging.getLogger(__name__).info(message.format(*args, **kw))

    def _get_results(self):
        def select_results(driver):
            results = driver.find_element_by_id(self.QUNIT_RESULTS_ID)
            failed = results.find_element_by_class_name(self.FAILED_CLASS)
            total = results.find_element_by_class_name(self.TOTAL_CLASS)
            return failed, total

        self._log("waiting for results with timeout {0}", self.timeout)
        wait = WebDriverWait(self.driver, self.timeout)
        failed, total = wait.until(select_results)
        self._log("{0} tests failed out of {1} total", failed, total)
        return int(failed), int(total)

    def _test(self):
        self._log("running test at {0}", self.url)
        self.driver.get(self.url)
        failed, total = self._get_results()
        if failed:
            raise TestFailedError("{0} tests failed".format(failed))
        elif total == 0:
            raise TestFailedError("no tests run")

    def run(self):
        """Execute the test."""
        self.driver = self._create_webdriver()
        try:
            self._test()
        finally:
            # Important!
            self._log("quitting webdriver")
            self.driver.quit()
        self.driver = None
