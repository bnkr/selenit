#!/usr/bin/python
import os, glob
from setuptools import setup, find_packages

setup(name="selenit", version="1.0.0",
      description="Selenium automation utilities.",
      long_description=open('README.rst').read(), license="MIT",
      author="James Webber", author_email="bunkerprivate@gmail.com",
      packages=find_packages(exclude=["tests", "tests.*"]),
      entry_points={
          'console_scripts': [
              'servequnit = servequnit.scripts:servequnit_main',
              'selenibench = selenibench.scripts:selenibench_main',
              'screenit = screenit.scripts:screenit_main',
           ],
      },
      url="http://github.com/bnkr/selenit",
      test_suite='tests')
