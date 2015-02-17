Selenit
=======

Selenium automation utilities.

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
  $ stat 001.png

See `--help` for more.

Future Work
~~~~~~~~~~~

* parallelism would be nice

* an html gallery of the images
