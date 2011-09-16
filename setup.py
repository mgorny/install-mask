#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2010 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from distutils.core import setup

import os.path, sys

sys.path.insert(0, os.path.dirname(__file__))
try:
	from installmask import PV
except ImportError:
	PV = 'unknown'

setup(
		name = 'install-mask',
		version = PV,
		author = 'Michał Górny',
		author_email = 'mgorny@gentoo.org',
		url = 'http://github.com/mgorny/install-mask',

		packages = ['installmask'],
		scripts = ['install-mask'],

		classifiers = [
			'Development Status :: 2 - Pre-Alpha',
			'Environment :: Console',
			'Intended Audience :: System Administrators',
			'License :: OSI Approved :: BSD License',
			'Operating System :: POSIX',
			'Programming Language :: Python',
			'Topic :: System :: Installation/Setup'
		]
)
