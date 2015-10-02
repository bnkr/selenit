#!/usr/bin/python
import os, glob
from setuptools import setup

def find_packages():
    here = os.path.dirname(os.path.realpath(__file__))
    lib = os.path.join(here, "servequnit", "**.py")
    packages = []
    for name in glob.glob(lib):
        if os.path.basename(name) == "__init__.py":
            name = os.path.dirname(name)
        else:
            name = os.path.splitext(name)[0]

        name.replace(here, "").replace(os.path.sep, ".")

    return packages

setup(name="selenit", version="1.0.0",
      description="Selenium automation utilities.",
      long_description=open('README.rst').read(), license="MIT",
      author="James Webber", author_email="bunkerprivate@gmail.com",
      package_dir={'servequnit': 'servequnit', 'selenibench': 'selenibench', 'screenit': 'screenit'}, 
      py_modules=find_packages(),
      entry_points={
          'console_scripts': [
              'servequnit = servequnit.scriprts:servequnit_main',
              'selenibench = selenibench.scriprts:selenibench_main',
              'screenit = screenit.scriprts:screenit_main',
           ],
      },
      url="http://github.com/bnkr/selenit",
      test_suite='tests')
