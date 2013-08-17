ServeQUnit
==========

Introduction
------------

ServeQUnit is a simple python HTTP server which serves the QUnit test runner
(probably others later) and your javascript.  Library functions are available to
embed the server in your tests and to interpret the test result using selenium.

Features
--------

* no need to write a runner html file for every test
* no need to have a special organisation of your js test files
* tests can be run in parallel
* easy to embed the http server in existing test cases

Command-line Usage
------------------

Start a server::

  $ servequnit -p 8081 -H localhost test.js
  $ sensible-browser http://localhost:8081/test/

The `/test/` prefix will serve a test which runs the script named by the
positional argument.

Serve test scripts from within a root directory::

  $ servequnit -p 8081 -H localhost --test-root app/tests
  $ sensible-browser http://localhost:8081/test/module/test.js

If there is no test root or test directory then the `/test/` url will use the
server's root.

Add library files to the document::

  $ servequnit --lib /static/pants.js

The `/static/` prefix will cause files to be read from the server's document
root which is determined by `--root` or pwd.

Map a url onto an arbitrary file::

  $ servequnit -p 8081 -H localhost \
    --read pants=test.js \
    --lib /read/pants

Run tests with selenium::

  $ servequnit --webdriver http://localhost:9092 test1.js test2.js

Server Library Usage
--------------------

Most usage should be possible by the single object::

  from servequnit.factory import js_server

Simple usage::

  with js_server.context(host="localhost") as server:
      urllib.urlopen(server.address).read()

You can also decorate a test method::

  @js_server.decorator(host="localhost")
  def test_something(self, server):
      urllib.urlopen(server.address).read()

Some more complicated settings might need this instead::

  from servequnit.factory import ServerFactory

  factory = ServerFactory(host="localhost").lib("something").lib("other")
  with factory.server_context() as server:
      urllib.urlopen(server.address).read()

Note that it is very important that the server's `wait_for_terminate` method is
called or test runners can deadlock at the end of executing all of your tests.
These contexts all do that for you.

Selenium Library Usage
----------------------

Not written yet.  Will look something like::

  run_qunit_test(**config)

Which is an alias for::

  with js_server(**config) as server:
      tester = QUnitSeleniumTester(server.address)
      tester.run()

So you can use the selenium tester against static content if you want.

Developing and Installing
-------------------------

Since not everyone uses buildout I'll explain it quickly.

Optionally set up a virtual environment.  This isolates dependencies and means
servequnit won't conflict with anything else (unless your system python
changes)::

  $ cd servequnit
  # --no-site-packages might be needed on older versions of virtualenv
  $ virtualenv venv
  # Sometimes not necessary but doesn't hurt.
  $ ./venv/bin/pip install -U setuptools

Required steps start here.  If you didn't make a virutalenv then use your system
python instead of the one in the virtualenv::

  # Download buildout
  $ ./venv/bin/python bootstrap.py
  # Install dependencies into ./eggs
  $ ./bin/buildout

The `./bin/python` script is now a python which will use your virtualenv and
also the local eggs downloaded by buildout.

You can now run servequnit without messing with your system at all.  The eggs
are re-locateable so if you re-write the `sys.path` changes you can package the
entire tree as a .deb or .rpm package if you want.
