Screenit
========

Introduction
------------

A simple python command-line program to screenshot a list of urls in batch using
a selenium webdriver.

Installation
------------

Screenit requires:

* argparse

* selenium

I suggest you use a virtual environment to do this::

  $ cd screenit # cloned source
  $ virtualenv venv
  $ venv/bin/pip install argparse
  $ venv/bin/pip install selenium
  $ venv/bin/python bin/screenit --help

Usage
-----

A simple example::

  $ screenit -w "http://localhost:4444/wd/hub" "http://google.com"
  $ stat 001.png

See `--help` for more.

Future Work
-----------

* parallelism would be nice

* an html gallery of the images
