#	vim:fileencoding=utf-8
# (c) 2010 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from optparse import OptionParser
import os, os.path, sys

from portage import create_trees

from flaggie.makeconf import MakeConf, NewVariable

from .locationdb import LocationDB

def expand_ldb(args, ldb):
	for a in args:
		if os.path.isabs(a):
			yield a
		else:
			for exp in ldb[a].paths:
				yield exp.pyval

def add(instmask, args, ldb):
	for a in expand_ldb(args, ldb):
		for t in instmask:
			if a in [fl.toString() for fl in t]:
				break
		else:
			for t in instmask:
				t.append(a)
				break
			else:
				raise AssertionError('Unreachable block of code reached')

def remove(instmask, args, ldb):
	args = tuple(expand_ldb(args, ldb))
	for t in instmask:
		for a in args:
			del t[a]

def info(instmask, args, ldb):
	if not args:
		print('Paths currently in INSTALL_MASK:')
	else:
		paths = set()

	foundone = False
	for t in instmask:
		for d in t:
			if not args:
				print('* %s' % d.toString())
			else:
				paths.add(d.toString())
			foundone = True

	if args:
		for a in args:
			if os.path.isabs(a):
				exp = (a,)
			else:
				try:
					e = ldb[a]
				except KeyError:
					print('* %s (invalid)' % a)
					exp = ()
				else:
					print('# %s [%s]' % (a,
						e.description or '(no description)'))
					exp = e.paths

			for aa in exp:
				print('* %s (%s)' % (aa,
					'enabled' if aa in paths else 'disabled'))
	elif not foundone:
		print('(none)')

def rebuild(instmask, args, ldb, dbapi):
	def _get_enabled(instmask):
		ret = set()
		for t in instmask:
			for d in t:
				ret.add(d.toString())
		return frozenset(ret)

	def _output_status(cur, length):
		sys.stderr.write('\rScanning packages: %4d of %4d...' % (cur, length))

	def _match_path(vpath, args, enabled):
		for p in args:
			if vpath.startswith(p):
				if bool(os.path.exists(vpath)) == bool(p in enabled):
					return True
		return False

	enabled = _get_enabled(instmask)
	if args:
		paths = frozenset(expand_ldb(args, ldb))
	else:
		paths = enabled

	cpvs = dbapi.cpv_all()
	cpvl = len(cpvs)
	rebuilds = set()
	for i, cpv in enumerate(cpvs):
		_output_status(i, cpvl)
		dblink = dbapi._dblink(cpv)

		for f in dblink.getcontents():
			if _match_path(f, paths, enabled):
				rebuilds.add(cpv)
				break

	_output_status(cpvl, cpvl)
	sys.stderr.write(' done.\n')

	for r in rebuilds:
		print('=%s' % r)

def main(argv):
	parser = OptionParser()
	parser.add_option('-a', '--add',
			dest='add', action='store_true', default=False,
			help='Add paths to INSTALL_MASK')
	parser.add_option('-d', '--delete', '--remove',
			dest='remove', action='store_true', default=False,
			help='Remove paths from INSTALL_MASK')
	parser.add_option('-i', '--info',
			dest='info', action='store_true', default=False,
			help='Print information about INSTALL_MASK flag or INSTALL_MASK in general')
	parser.add_option('-r', '--rebuild',
			dest='rebuild', action='store_true', default=False,
			help='Create rebuild list for packages not matching given (or current) INSTALL_MASK')
	(opts, args) = parser.parse_args(argv[1:])

	acts = opts.add + opts.remove + opts.info + opts.rebuild
	if acts > 1:
		parser.error('Actions (-a, -d, -i, -r) are mutually exclusive.')
	elif acts < 1:
		parser.error('No action specified (-a, -d, -i, -r).')
	if not args and not opts.info + opts.rebuild:
		parser.error('No paths specified')

	trees = create_trees(
			config_root = os.environ.get('PORTAGE_CONFIGROOT'),
			target_root = os.environ.get('ROOT'))
	porttree = trees[max(trees)]['porttree'].dbapi
	vartree = trees[max(trees)]['vartree'].dbapi

	confroot = os.environ.get('PORTAGE_CONFIGROOT', '/')
	mkconf = MakeConf(
		(os.path.join(confroot, 'etc', 'make.conf'),
			os.path.join(confroot, 'etc', 'portage', 'make.conf')),
		porttree)

	# .cp_list() should be potentially faster than .match()
	for m in reversed(porttree.cp_list('app-portage/install-mask')):
		d = os.path.dirname(porttree.findname(m))
		dbf = os.path.join(d, 'files', 'location-db.xml')
		if os.path.exists(dbf):
			break
	else:
		dbf = None
	ldb = LocationDB(dbf)

	try:
		installmask = mkconf.variables['INSTALL_MASK']
	except KeyError:
		installmask = NewVariable('INSTALL_MASK')
		mkconf.newvars.append(installmask)

	try:
		if opts.add:
			add(installmask, args, ldb = ldb)
		elif opts.remove:
			remove(installmask, args, ldb = ldb)
		elif opts.info:
			info(installmask, args, ldb = ldb)
		elif opts.rebuild:
			rebuild(installmask, args, ldb = ldb, dbapi = vartree)
	except Exception as e:
		parser.error(str(e))

	mkconf.write()
