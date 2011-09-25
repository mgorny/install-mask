#	vim:fileencoding=utf-8
# (c) 2010 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from collections import namedtuple

import lxml.objectify, lxml.etree

Location = namedtuple('Location', ('paths', 'description'))

class LocationDB(object):
	def __init__(self, path):
		self._path = path
		self._loaded = False

	def _load_db(self):
		if not self._loaded:
			if self._path is None:
				raise SystemError('location-db.xml not found in any FILESDIR!')

			schema = lxml.etree.RelaxNG(lxml.etree.XML(ldb_schema))
			t = lxml.objectify.parse(self._path)
			schema.assertValid(t)
			self._root = t.getroot()
			self._loaded = True

	def __getitem__(self, key):
		self._load_db()
		for l in self._root.location:
			if l.get('id') == key:
				try:
					d = ' '.join(l.description.text.split())
				except AttributeError:
					d = None
				return Location(tuple(l.path), d)
		raise KeyError('%s is an invalid location' % key)

ldb_schema = '''

<element name="install-mask" xmlns="http://relaxng.org/ns/structure/1.0"
		datatypeLibrary="http://www.w3.org/2001/XMLSchema-datatypes">
	<zeroOrMore>
		<element name="location">
			<interleave>
				<oneOrMore>
					<element name="path"><text/></element>
				</oneOrMore>
				<optional>
					<element name="description"><data type="token"/></element>
				</optional>
			</interleave>

			<attribute name="id"><data type="ID"/></attribute>
		</element>
	</zeroOrMore>
</element>

'''
