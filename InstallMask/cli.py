#	vim:fileencoding=utf-8
# (c) 2010 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 3-clause BSD license.

from optparse import OptionParser
import os

from portage import create_trees
from portage.const import MAKE_CONF_FILE, USER_CONFIG_PATH

from flaggie.makeconf import MakeConf

def add(instmask, args):
	for a in args:
		for t in instmask:
			if a in t:
				break
		else:
			for t in instmask:
				t.append(a)
				break
			else:
				raise AssertionError('Unreachable block of code reached')

def remove(instmask, args):
	for t in instmask:
		for a in args:
			del t[a]

def main(argv):
	parser = OptionParser()
	parser.add_option('-a', '--add',
			dest='add', action='store_true',
			help='Add paths to INSTALL_MASK')
	parser.add_option('-d', '--delete', '--remove',
			dest='remove', action='store_true',
			help='Remove paths from INSTALL_MASK')
	(opts, args) = parser.parse_args(argv[1:])
	if opts.add and opts.remove:
		parser.error('Options --add and --remove are mutually exclusive.')
	elif not opts.add and not opts.remove:
		parser.error('No action specified (--add or --remove).')
	if not args:
		parser.error('No paths specified')

	trees = create_trees(
			config_root = os.environ.get('PORTAGE_CONFIGROOT'),
			target_root = os.environ.get('ROOT'))
	porttree = trees[max(trees)]['porttree'].dbapi

	confroot = porttree.settings['PORTAGE_CONFIGROOT']
	usercpath = os.path.join(confroot, USER_CONFIG_PATH)
	mkconf = MakeConf(
		(os.path.join(confroot, MAKE_CONF_FILE),
			os.path.join(usercpath, 'make.conf')),
		porttree)

	# XXX: NewVariable, blah, blah
	installmask = mkconf.variables['INSTALL_MASK']
	if opts.add:
		add(installmask, args)
	elif opts.remove:
		remove(installmask, args)

	mkconf.write()
