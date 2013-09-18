import os
from unittest import TestCase
from mock import Mock
from servequnit.factory import ServerFactory
from servequnit.tester import QunitSeleniumTester, TestFailedError


class FakeElement(object):
    def __init__(self, driver, text):
        self.driver = driver
        self.text = str(text)

    def find_element_by_id(self, id):
        return self.driver.find_element_by_id(id)

    def find_element_by_class_name(self, css_class):
        return self.driver.find_element_by_class_name(css_class)

class FakeSelenium(object):
    def __init__(self, **kw):
        self.constructor_args = kw
        self.mock_data = {'id': {}, 'class': {}}

    def get(self, url):
        pass

    def find_element_by_id(self, id):
        data = self.mock_data['id'][id]
        return FakeElement(self, data)

    def find_element_by_class_name(self, css_class):
        data = self.mock_data['class'][css_class]
        return FakeElement(self, data)

    def quit(self):
        pass

    def mock_results(self, failed, total):
        container = QunitSeleniumTester.QUNIT_RESULTS_ID

        self.mock_data['id'][container] = ""
        self.mock_data['class'][QunitSeleniumTester.FAILED_CLASS] = failed
        self.mock_data['class'][QunitSeleniumTester.TOTAL_CLASS] = total

class QunitSeleniumTesterTestCase(TestCase):
    use_real_selenium = 'SERVEQUNIT_TEST_REAL_SELENIUMN' in os.environ

    def _make_tester(self, server, suffix=None, webdriver=None):
        if self.use_real_selenium:
            get_driver = None
        elif webdriver:
            get_driver = lambda **kw: webdriver
        else:
            raise Exception("fake webdriver is required if not testing "
                            "against real selenium")
        suffix = suffix or "test/"
        url = server.url + suffix
        hub = "http://127.0.0.1:4444/wd/hub"
        tester = QunitSeleniumTester(
            url=url, hub=hub,
            capabilities={'browserName': "firefox"},
            selenium_factory=get_driver)
        return tester

    def test_passing_test_passes(self):
        driver = FakeSelenium()
        driver.mock_results(failed=0, total=1)

        test_file = os.path.join(os.path.dirname(__file__), "data", "passes.js")
        factory = ServerFactory().bind_script("test", test_file)
        with factory.run() as server:
            tester = self._make_tester(server, webdriver=driver)
            tester.run()

    def test_failing_test_reports_failure(self):
        driver = FakeSelenium()
        driver.mock_results(failed=1, total=2)

        test_file = os.path.join(os.path.dirname(__file__), "data", "fails.js")
        factory = ServerFactory().bind_script("test", test_file)
        with factory.run() as server:
            tester = self._make_tester(server, webdriver=driver)
            self.assertRaises(TestFailedError, tester.run)

    def test_empty_test_reports_no_tests(self):
        driver = FakeSelenium()
        driver.mock_results(failed=0, total=0)
        factory = ServerFactory().bind_script("test", "/dev/null")
        with factory.run() as server:
            tester = self._make_tester(server, webdriver=driver)
            self.assertRaises(TestFailedError, tester.run)
