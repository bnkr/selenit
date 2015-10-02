#!/usr/bin/python
import os, glob
from setuptools import setup

setup(name="selenit", version="1.0.0",
      description="Selenium automation utilities.",
      long_description=open('README.rst').read(), license="MIT",
      author="James Webber", author_email="bunkerprivate@gmail.com",
      package_dir={'servequnit': 'servequnit', 'selenibench': 'selenibench', 'screenit': 'screenit'}, 
      entry_points={
          'console_scripts': [
              'servequnit = servequnit.scriprts:servequnit_main',
              'selenibench = selenibench.scriprts:selenibench_main',
              'screenit = screenit.scriprts:screenit_main',
           ],
      },
      url="http://github.com/bnkr/selenit",
      test_suite='tests')
