import logging
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Remote as WebdriverRemote
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait

class TestFailedError(Exception):
    pass

class TestResult(object):
    """DTO explaining the test result."""

    def __init__(self):
        self.total = 0
        self.failed = 0
        self.timeout = False

class QunitSeleniumTester(object):
    """Runs selenium tests against an arbitrary http location which serves a
    qunit test page."""
    FailureError = TestFailedError

    QUNIT_RESULTS_ID = "qunit-testresult"
    FAILED_CLASS = "failed"
    TOTAL_CLASS = "total"

    def __init__(self, url, hub, timeout=None, capabilities=None,
                 selenium_factory=None):
        self.url = url
        self.hub = hub
        self.capabilities = capabilities or {}
        self.driver = None
        self.timeout = timeout or 5
        self.factory = selenium_factory or WebdriverRemote

    def _log(self, message, *args, **kw):
        logging.getLogger(__name__).info(message.format(*args, **kw))

    def _create_webdriver(self):
        self._log("connecting to selenium at {0}", self.hub)
        driver = self.factory(command_executor=self.hub,
                              desired_capabilities=self.capabilities)
        self.driver = driver
        return driver

    def _get_results(self):
        def select_results(driver):
            results = driver.find_element_by_id(self.QUNIT_RESULTS_ID)
            failed = results.find_element_by_class_name(self.FAILED_CLASS)
            total = results.find_element_by_class_name(self.TOTAL_CLASS)
            return failed, total

        self._log("waiting for results with timeout {0}", self.timeout)
        wait = WebDriverWait(self.driver, self.timeout)
        failed, total = wait.until(select_results)
        return int(failed.text), int(total.text)

    def _test(self):
        self._log("running test at {0}", self.url)
        # TODO: deal with non 200
        self.driver.get(self.url)

        try:
            failed, total = self._get_results()
            self._log("{0} tests failed out of {1} total", failed, total)
        except TimeoutException:
            raise TestFailedError("timed out waiting for results")

        return failed, total

    def _test_or_screenshot(self):
        try:
            failed, total = self._test()
            if failed:
                raise TestFailedError("{0} tests failed".format(failed))
            elif total == 0:
                raise TestFailedError("no tests run")
        except TestFailedError:
            # TODO: take a screendump here
            raise

    def run(self):
        """Execute the test."""
        self.driver = self._create_webdriver()
        try:
            return self._test_or_screenshot()
        finally:
            # Important!
            self._log("quitting webdriver")
            self.driver.quit()
            self.driver = None
