from routes import routes
from parsedocs import docs2dict

def helping(cmd, api, istty):
	"""call: 'help [COMMAND]'
	description: 'Print help on the given command. If no command is given, prints a list of commands.'
	args: 'COMMAND: Optional arg. If given, it specifies a command to print detailed help on.
	      .In general, the name of a command is the part of the command before the first arg, eg: "create vm", "console".'
	errors: 'Command not found: Returns exit code 3'
	"""

	# Note: mostly not affected by istty as its assumed that if the user is asking for help, they want stuff to be output.

	if cmd == None:
		cmd = ''

	if not cmd:
		print
		print 'Command listing:'
		for name, regex, func in routes:
			print docs2dict(func.__doc__)['call']
		print
		print 'For more detailed help, run "help COMMAND"'
		print 'where COMMAND is the first part of a command, eg. "show ips" or "create vm"'
		return 0

	for name, regex, func in routes+[('help',None,helping)]:
		if name == cmd:
			info = docs2dict(func.__doc__)
			print
			print info['call']
			if 'description' in info:
				print
				print info['description']
			if 'args' in info:
				print
				print info['args']
			if 'output' in info:
				print
				print 'In quiet mode, this function will output in the following format:'
				print info['output']
			if 'errors' in info:
				print
				print 'The following errors have special return codes:'
				print info['errors']
			return 0

	if istty:
		print 'No command found: %s' % cmd
	return 3
