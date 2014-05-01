#!/usr/bin/env python

DEBUG=False # Change this to true to have --debug by default. Useful if code is failing before option parsing is reached.

import sys
import re
import os
import getpass
import sys
from getopt import gnu_getopt, GetoptError
from ovm_ctl import routes
from ovm_ctl.webbindings import apibindings, extra_r, HTTPException
from ovm_ctl.helping import helping
from ovm_ctl.parsedocs import docs2dict

def quit(*args):
	"""call: 'quit'
	description: 'Exit the program. Has no effect if given in command line options.
	             .Note that an EOF (Ctrl-D) or blank line can also be used to exit.'
	"""
	sys.exit(0)

def notimp(*args):
	print "Not implemented"

routes = routes.routes + \
 	[('help', r'^help(?: (.*))?$', helping)]

croutes = [(re.compile(pattern), fun) for padding, pattern, fun in routes + extra_r]

MIN_CLOSENESS = 4 # Min leading characters to match before deciding to print a "did you mean"

def cmd_parse(api, cmd, istty):
	for cpattern, fun in croutes:
		match = cpattern.match(cmd.strip())
		if not match:
			continue
		groups = match.groups()
		groups = list(groups) + [istty, api]
		try:
			ret = fun(*groups)
			if ret == None: # No return -> success
				ret = 0
			return ret
		except Exception, ex:
			if istty:
				print """Unknown error. Command failed.
Error message: "%s"
Maybe the web API is inaccessible, or your credentials are wrong.
If you are trying to do something to a disk or IP, you may have to detach it first.
Most operations on a vm can only be done while it is shut down.""" % str(ex)
			if DEBUG:
				raise
			return 2

	if istty:
		did_you_mean(cmd, routes)
	return 1

def did_you_mean(cmd, routes):
	"""Print a message along the lines of "did you mean: blah" or "blah not formatted correctly",
	by trying to match the beginning of cmd to the fixed beginnings of each command"""
	best = []
	bestlength = 0
	for fixedstr, pattern, func in routes:
		for l in range(len(fixedstr))[::-1]:
			if cmd.startswith(fixedstr[:l+1]):
				if l+1 > bestlength:
					best = [(fixedstr, func.__doc__)]
					bestlength = l+1
				elif l+1 == bestlength:
					best += [(fixedstr, func.__doc__)]
				break
	for x in best:
		if bestlength == len(x[0]): # if prefix matches the whole fixedstr
			print 'Command incorrectly formatted'
			print 'Basic usage: %s' % docs2dict(x[1])['call']
			print 'For more information, try "help %s"' % x[0]
			return
	print 'Command not found.'
	if bestlength >= MIN_CLOSENESS:
		print 'Did you mean:'
		for x in best:
			print docs2dict(x[1])['call']

def repl(api, istty):
	if istty:
		try:
			print "Hi %(firstname)s %(lastname)s!" % api.details()
		except Exception:
			pass
		print "Welcome to the OrionVM command line bindings. For more information please type help."
		print "For full documentation exit the program and run 'man ovm-ctl'."
	while 1:
		try:
			cmd = raw_input(istty and ">> " or "")
		except EOFError:
			return 0

		ret = cmd_parse(api, cmd, istty)
		if not istty and ret:
			return ret

def get_creds(isatty, credfile, user=None, pswd=None):
	from_file = False
	user_from_file = False
	pswd_from_file = False
	asksave = False
	if not user:
		if os.path.exists(credfile):
			creds = open(credfile, 'rU').read()
			creds = creds.split("\n")
			if len(creds) > 0 and creds[0] != '':
				user = creds[0]
				user_from_file = user != ''
			if len(creds) > 1 and creds[1] != '':
				pswd = creds[1]
				pswd_from_file = pswd != ''
			from_file = user_from_file and pswd_from_file

	if not user:
		user = raw_input("Username: ")
		asksave = True

	if not pswd:
		if isatty and user_from_file:
			print "Username: %s" % user
		pswd = getpass.getpass("Password: ")

	# Only ask to save if default credfile doesn't exist, no other credfile given, user is not blank.
	if user and isatty and asksave:
		while True:
			response = raw_input("Would you like to save your username as the default? [yes/no/never] > ")
			if response == 'yes':
				credfd = open(credfile, 'w')
				if os.name == 'posix':
					os.chmod(credfile, 0600)
				credfd.write(user+'\n')
				while True:
					response = raw_input("Also save your password (this may not be secure)? [yes/no] > ")
					if response not in ('yes', 'no'):
						continue
					if response == 'yes':
						credfd.write(pswd+'\n')
					credfd.close()
					break
				break
			elif response == 'never':
				open(credfile, 'w') # Touch to create blank file
				if os.name == 'posix':
					os.chmod(credfile, 0600)
				break
			elif response == 'no':
				break

	return (user, pswd, from_file)

def creds(isatty, user=None, pswd=None, credfile=None):
	if credfile == None:
		credfile = os.path.expanduser("~/.orionauth")
	
	while 1:
		user, pswd, from_file = get_creds(isatty, credfile, user=user, pswd=pswd)
		api = apibindings(user, pswd)
		try:
			api.details()
			return (user, pswd)
		
		except HTTPException, e:
			if e.retcode == 401:
				if not isatty:
					raise

				user = None
				pswd = None	

				if from_file:
					try:
						os.remove(credfile)
					except OSError:
						raise Exception("Invalid userame and/or password in auth file %s" % credfile)
				else:
					print "Invalid username and/or password"
			
			else:
				raise

# Dict of distinct options, where each entry is identifier:([short names], [long names], argname, docstring)
# with argname = '' for no args
options = {
	'user': (['u'], ['user', 'username', 'auth'], 'user[:pass]', "If given, specifies an OrionVM account to log in as. Optionally, the password can also be given, seperated from the username by a colon. This option overrides anything read from an authfile."),
	'authfile': (['a'], ['authfile'], 'filename', "Use the given file as the authfile (see Authentication) instead of the default."),
	'file': (['f'], ['file'], 'filename', "Read a list of commands from a file, instead of stdin. Implies -q unless overriden with -v. Note that options are processed in the order they are given and any later option overrides an earlier one."),
	'verbose': (['v'], ['verbose'], '', "Force verbose mode even when stdin or stdout is not a tty. Causes the program to generate human-readable outputs."),
	'quiet': (['q'], ['quiet'], '', "Force quiet mode even when stdin and stdout are a tty. Causes the program to generate little or no output."),
	'debug': ([], ['debug'], '', "Report the underlying exceptions in the python code. This option is intended only for debugging a problem after editing the code.") # Debug mode (don't catch errors)
}

def getopt_values():
	"""Return (short_opts, long_opts):
		short_opts: a string for shortopts suitable for getopts
		long_opts: a list for longopts also suitable for getopts"""
	short_opts = ''
	long_opts = []
	for shorts, longs, needs_arg, doc in options.values():
		for short_opt in shorts:
			short_opts += short_opt
			if needs_arg:
				short_opts += ':'
		if needs_arg:
			longs = [opt + '=' for opt in longs]
		long_opts += longs
	return (short_opts, long_opts)

def match_opt(opt, opt_name):
	"""Returns true if opt is one of the options listed under opt_name in options"""
	opt = opt[1:] # opt may be '-x' or '--abc', now is 'x' or '-abc'
	if opt in options[opt_name][0]:
		return True
	opt = opt[1:] # if short, is now ''. if long, is now 'abc'
	return opt in options[opt_name][1]

def main(args, istty):
	short_opts, long_opts = getopt_values()
	authfile = None
	user = None
	pswd = None

	try:
		opts, args = gnu_getopt(args, short_opts, long_opts)
	except GetoptError, ex:
		if istty:
			print 'Error parsing command line arguments: %s' % str(ex)
		return 1

	read_from_file = None
	for opt, value in opts:
		if match_opt(opt, 'verbose'):
			istty = True
		elif match_opt(opt, 'quiet'):
			istty = False
		elif match_opt(opt, 'user'):
			if ':' in value:
				user, pswd = value.split(':')
			else:
				user = value
		elif match_opt(opt, 'authfile'):
			authfile = value
		elif match_opt(opt, 'debug'):
			global DEBUG
			DEBUG = True
		elif match_opt(opt, 'file'):
			try:
				if value.startswith("./"):
					value = value[2:]
				read_from_file = open(value, 'rU')
			except IOError:
				print 'Could not open file "%s" for reading.' % value
				raise
			istty = False
		else:
			if istty:
				print 'Warning: option %s not implemented' % opt

	user, pswd = creds(istty, user, pswd, authfile)

	if read_from_file:
		sys.stdin = read_from_file

	api = apibindings(user, pswd)
	if args != []: # got cmdline args
		cmd = " ".join(args)
		ret = cmd_parse(api, cmd, istty)
		return ret
	else:
		return repl(api, istty)

if __name__ == "__main__":
	istty = sys.stdout.isatty() and sys.stdin.isatty()
	try:
		sys.exit(main(sys.argv[1:], istty))
	except SystemExit:
		raise
	except BaseException, ex:
		if DEBUG:
			if isinstance(ex, HTTPException):
				print 'DEBUG: Recieved response from web server:'
				print ex.response
			raise
		if istty:
			print 'An error occurred. Perhaps the api is inaccessible?'
			print ex
		sys.exit(2)
