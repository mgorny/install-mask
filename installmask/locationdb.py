#	vim:fileencoding=utf-8
# (c) 2010 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from collections import namedtuple
import io, shlex

try:
	from configparser import NoOptionError

	# 3.2+
	if hasattr(configparser.ConfigParser, 'read_file'):
		from configparser import ConfigParser
	else:
		from configparser import SafeConfigParser as ConfigParser
		setattr(ConfigParser, 'read_file', ConfigParser.readfp)
except ImportError:
	from ConfigParser import NoOptionError
	from ConfigParser import SafeConfigParser as ConfigParser
	setattr(ConfigParser, 'read_file', ConfigParser.readfp)


Location = namedtuple('Location', ('paths', 'description'))

class LocationDB(object):
	def __init__(self, path):
		self._path = path
		self._loaded = False

	def _load_db(self):
		if not self._loaded:
			if self._path is None:
				raise SystemError('location-db.conf not found in any FILESDIR!')

			with io.open(self._path, encoding='utf-8') as f:
				self._conf = ConfigParser()
				self._conf.read_file(f)

			try:
				if self._conf.get('__install-mask__', 'version') != '1':
					raise SystemError('Unsupported location-db.conf version')
			except (KeyError, NoOptionError):
				raise SystemError('Malformed location-db.conf')

	def __getitem__(self, key):
		self._load_db()

		try:
			path = shlex.split(self._conf.get(key, 'path'))
		except KeyError:
			raise KeyError('%s is an invalid location' % key)

		try:
			desc = self._conf.get(key, 'description')
		except NoOptionError:
			desc = None

		return Location(tuple(path), desc)
