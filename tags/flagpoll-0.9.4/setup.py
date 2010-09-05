#!/usr/bin/env python

from distutils.core import setup
try:
   import py2exe
except:
   pass

setup(
      name='flagpoll',
      version='0.9.4',
      description='Flagpoll is a tool for developers to use meta-data files for storing information on what is needed to compile their software.',
      author='Daniel E. Shipton',
      author_email='dshipton@infiscape.com',
      license='GPL',
      url='http://code.google.com/p/flagpoll/',
      download_url='http://code.google.com/p/flagpoll/downloads/list',
      console=['flagpoll'],
      scripts=['flagpoll'],
      long_description = "Flagpoll is a tool for developers to use meta-data files for storing information on what is needed to compile their software. Think of it as the rpm of software development. It enables developers total control over which packages, versions, architectures, etc. that they want to use meta-data from.",
      data_files=[('share/flagpoll', ['flagpoll.fpc']), ('share/man/man1', ['flagpoll.1']), ('share/aclocal', ['flagpoll.m4']), ('share/html', ['flagpoll-manual.html'])]
      )
