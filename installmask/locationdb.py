#	vim:fileencoding=utf-8
# (c) 2010 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from collections import namedtuple

import lxml.objectify, lxml.etree

Location = namedtuple('Location', ('paths', 'description'))

class LocationDB(object):
	def __init__(self, path):
		# XXX: make this lazy
		schema = lxml.etree.XMLSchema(lxml.etree.XML(ldb_schema))
		p = lxml.objectify.makeparser(schema = schema)
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
		raise KeyError('%s is an invalid location' % key)

ldb_schema = '''

<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
	<xs:element name="install-mask">
		<xs:complexType>
			<xs:sequence>
				<xs:element name="location" minOccurs="0" maxOccurs="unbounded">
					<xs:complexType>
						<xs:sequence>
							<xs:element name="path" type="xs:string" maxOccurs="unbounded"/>
							<xs:element name="description" type="xs:token" minOccurs="0"/>
						</xs:sequence>

						<xs:attribute name="id" type="xs:string" use="required"/>
					</xs:complexType>
				</xs:element>
			</xs:sequence>
		</xs:complexType>
	</xs:element>
</xs:schema>

'''
