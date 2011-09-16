#	vim:fileencoding=utf-8
# (c) 2010 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from collections import namedtuple

import lxml.objectify

Location = namedtuple('Location', ('paths', 'description'))

class LocationDB(object):
	def __init__(self, path):
		# XXX: make this lazy
		p = lxml.objectify.makeparser(dtd_validation = True)
		t = lxml.objectify.parse(path, p)
		self._root = t.getroot()

	def __getitem__(self, key):
		for l in self._root.location:
			if l.get('id') == key:
				try:
					d = ' '.join(l.description.text.split())
				except AttributeError:
					d = None
				return Location(tuple(l.path), d)
		raise KeyError('%s not found in LocationDB' % key)
