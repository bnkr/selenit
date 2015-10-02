#!/usr/bin/python
import os, glob
from distutils.core import setup

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

setup(name="servequnit", version="1.0.0",
      description="Run browser-based javascript unit tests.",
      long_description=open('README.rst').read(), license="MIT",
      author="James Webber", author_email="bunkerprivate@gmail.com",
      packages=['servequnit'], py_modules=find_packages(),
      scripts=['scripts/servequnit',],
      url="http://github.com/bnkr/servequnit",)
