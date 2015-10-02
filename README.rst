Selenit
=======

Selenium automation utilities.

.. image:: https://travis-ci.org/bnkr/servequnit.png?branch=master
  :target: https://travis-ci.org/bnkr/servequnit

Installation
------------

Screenit requires:

* argparse

* selenium

I suggest you use a virtual environment to do this::

  $ cd screenit # cloned source
  $ virtualenv venv
  $ venv/bin/pip install -r requirements.txt
  $ venv/bin/python setup,py develop
  $ venv/bin/screenit --help

Test coverage can be generated something like this::

  nosetests --with-coverage --cover-package=servequnit --cover-html --cover-html-dir=./coverage-output --cover-tests

Selenibench
-----------

An attempt at automating browsers for performance testing.

Essentially this is to make the process faster, not necessarily better.
Benchmarking websites is something which selenium is not really that great for
because you don't really get enough data but you can get some decent profiling
done.

Note that networking makes a big difference here.  Consider changing the packet
scheduler on your selenium machine to match the kind of users you are optimising
for::

  # Add 150ms delay to every packet on eth0.
  tc qdisc add dev eth0 root netem delay 150ms

Screenit
--------

A simple python command-line program to screenshot a list of urls in batch using
a selenium webdriver.

A simple example::

  $ screenit -w "http://localhost:4444/wd/hub" "http://google.com"
  $ stat google.com.png

See `--help` for more.

Future Work
~~~~~~~~~~~

* parallelism would be nice

* an html gallery of the images

ServeQUnit
----------

ServeQUnit is a simple python HTTP server which serves the QUnit test runner
(probably others later) and your javascript.  Library functions are available to
embed the server in your tests and to interpret the test result using selenium.

Features
~~~~~~~~

* no need to write a runner html file for every test
* no need to have a special organisation of your js test files
* tests can be run in parallel
* easy to embed the http server in existing test cases

Command-line Usage
~~~~~~~~~~~~~~~~~~

Start a server::

  $ servequnit -p 8081 -H localhost test.js
  $ sensible-browser http://localhost:8081/test/

The `/test/` prefix will serve a test which runs the script named by the
positional argument.

Serve test scripts from within a root directory::

  $ servequnit -p 8081 -H localhost --root app/tests
  $ sensible-browser http://localhost:8081/test/module/test.js

If there is no test root or test directory then the `/test/` url will use the
server's root.

Add library files to the document::

  $ servequnit pants.js

The `/static/` prefix will cause files to be read from the server's document
root which is determined by `--doc-root` or pwd.

Map a url onto an arbitrary file::

  $ servequnit -p 8081 -H localhost pants=outside-of-root.js

Selenium Usage
~~~~~~~~~~~~~~

Get seleium and its dependencies::

  $ wget http://selenium.googlecode.com/files/selenium-server-standalone-2.35.0.jar
  # aptitude install -y default-jre-headless
  $ java -jar selenium-server-standalone-2.35.0.jar

Xvfb is useful for automating tests without having browsers pop up::

  $ DISPLAY=:1 xvfb-run java -jar selenium-server-standalone-2.35.0.jar

Execute the test::

  $ servequnit --webdriver http://127.0.0.1:4444/wd/hub test1.js test2.js

Server Library Usage
~~~~~~~~~~~~~~~~~~~~

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

  factory = ServerFactory(host="localhost").script("something").script("other")
  with factory.server_context() as server:
      urllib.urlopen(server.address).read()

Note that it is very important that the server's `wait_for_stop` method is
called or test runners can deadlock at the end of executing all of your tests.
These contexts all do that for you.

Selenium Library Usage
~~~~~~~~~~~~~~~~~~~~~~

Not written yet.  Will look something like::

  run_qunit_test(**config)

Which is an alias for::

  with js_server.context(**config) as server:
      tester = QUnitSeleniumTester(url=server.address)
      tester.run()

So you can use the selenium tester against static content if you want.

Related Stuff
~~~~~~~~~~~~~

grunt-qunit-phantomjs
^^^^^^^^^^^^^^^^^^^^^

With Grunt you can run qunit tests without selenium (or any kind of server) at
all.  It uses a phantom browser.

PyVirtualDisplay
^^^^^^^^^^^^^^^^

Wraps xvfb.  Can be useful for creating displays of different resolution on the
fly.
