
"""Generates docs from function docstrings"""

# Oh hai there. This script is used to create the man page. It's kinda dirty. Really dirty.
# You shouldn't need to touch this or man_writing.py, they never get used by ovm-ctl proper.
# If you've made changes to stuff in other py files and would like the man page to reflect the changes,
# run "python gen_docs.py > /usr/share/man/man1/ovm-ctl.1" and it should just happen.

from parsedocs import docs2dict
from bindings import routes # import from bindings so we get the extra commands that bindings tacks on
from bindings import options
from man_writing import *
import re

def man_page():
	"""Return a string that is the man page for ovm-ctl(1)"""
	options['user'] = options['user'][:2] + (r'user\fR[\fB:\fIpass\fR]\fI',) + options['user'][3:] # Formatting for user's arg string

	result = title('ovm-ctl', section=1, source='OrionVM', manual='"OrionVM User Documentation"')

	result += heading('NAME') + "ovm-ctl \- command line interface to OrionVM Online API\n"

	result += heading('SYNOPSIS') + gen_synopsis('ovm-ctl', options.values(), optional_args=["command"])

	result += heading('DESCRIPTION') + \
r"""This is a program designed to be a command line interface to the OrionVM Online API calls.
It allows you to use simple commands to interact with and control your OrionVM account and resources.
A single command can be specified on the command line, or you can run it without commands to start
an interactive shell where commands can be typed.
""" + parbreak() + \
r"""The program has two output modes: verbose and quiet.
In verbose mode, human readable output is given.
In contrast, quiet mode is designed for scripts and the like.
Most commands will not produce output in quiet mode.
Errors must be detected by examining the program's exit code.
Commands that return information, such as the
""" + bold('show') + r"""family of commands, return a simple, machine-readable format.
See""" + '\n' + italic('COMMANDS') + "below for details.\n" + parbreak() + \
"By default (but see\n" + italic('OPTIONS') + r"""below) the program is in verbose mode.
However, if input or output is not a terminal (for example, it is a file or a pipeline), quiet mode is used.
""" + parbreak() + \
"For help with commands, see section\n" + italic('COMMANDS') + "below.\n"

	result += heading('Authentication', level=1) + \
r"""When the program is started (in verbose or quiet mode), the user is prompted for their
OrionVM login email and password. This step can be avoided by either giving a username on the command line (see
""" + italic('OPTIONS', suffix=')') + r"""or by writing an authfile.
The first time you give your credentials, the program will ask if you want to save them.
This will write an authfile for you in the default authfile location
""" + italic('~/.orionauth', '(', ').') + r"""The following is details on writing an authfile yourself.
""" + parbreak() + \
r"""An authfile is a plain text file containing one or two lines.
The first line is your OrionVM login email.
The second is your password.
If there is no second line or it is blank, your password will still be prompted for when the program is run.
Please consider the security risks of keeping your password stored in plaintext in a file on your system.
""" + parbreak() + \
r"""The program by default searches for a file called
""" + italic('.orionauth') + r"""in your home directory - you should place your authfile here
to have it be used automatically.
"""

	result += heading('Errors in interactive mode', level=1) + \
r"""When reading commands from input (ie. no command was supplied as an argument),
the effects of an error occurring depend on whether the program is running in verbose mode.
In verbose mode, the error is reported and execution continues.
In quiet mode, execution is aborted and the program exits with the exit status of the command that failed.
"""

	result += heading('OPTIONS') + man_format_options(options)

	result += heading('COMMANDS') + man_format_routes(routes)

	result += heading('EXIT STATUS') + \
heading('0', level=2) + "Command completed successfully (for a command given as an argument).\n" + \
heading('0', level=2) + "Program reached quit command or end of input (for reading commands from input).\n" + \
heading('1', level=2) + "Error in parsing command line arguments, or command not found.\n" + \
heading('2', level=2) + r"""Unknown error. Common causes include but are not limited to
incorrect authentication, internet connectivity issues or an invalid operation
(such as trying to delete a locked disk).""" + '\n' + \
heading('3-64', level=2) + "Reserved for command-specific errors. See section\n" + italic('COMMANDS') + "for details.\n"

	result += heading('FILES') + \
heading('~/.orionauth', level=2) + "Default authentication file. See subsection\n" + italic('Authentication') + "for details.\n"

	result += heading('NOTES') + \
"""In the current implementation of 
""" + bold('ovm-ctl console', suffix=',') + """the user's OrionVM password
is passed to
""" + bold('ssh', suffix='(1)') + r"""as a command line argument.
This means that the password is readable, in plaintext, to all users of the computer.
Please avoid using the command on a computer where other people may have access to the process list.
Note that this applies only to 
""" + bold('ovm-ctl', suffix=',') + r"""and the web panel in-browser console is completely safe.
"""

	return check_result(result.strip())

def man_format_options(options):
	"""Generate man formatting text for the options dict given.
	Options dict is as defined in bindings.py"""
	result = ''
	for shorts, longs, arg, doc in options.values():
		result += '.TP\n' # In a .TP, everything on the next line becomes the heading
		aliases = ['-'+x for x in shorts] + ['--'+x for x in longs]
		for opt in aliases[:-1]:
			result += r'\fB%s' % opt
			if arg:
				result += r' \fI%s' % arg
			result += r'\fR, '
		opt = aliases[-1]
		result += r'\fB%s' % opt
		if arg:
			result += r' \fI%s' % arg
		result += '\\fR\n'
		result += fix_text(doc)
	return result

def man_format_routes(routes):
	"""Generate man formatting text for the routes list given.
	Routes list is as defined in routes.py"""
	findargs = re.compile(r'([A-Z]+):((?:[ \t].*\n)+)') # An re for splitting the 'args' part of the docs
	result = 'Note: For commands that produce output in quiet mode, their entries contain formatting strings. These formatting strings describe the output as per the rules used by\n' + bold('printf',suffix='(3)')
	for name, pattern, func in routes:
		docs = docs2dict(func.__doc__)
		words = docs['call'].split(' ')
		words = [r'\f%s%s' % (word.isupper() and 'I' or 'B', word) for word in words] # Italic all isupper words, else bold.
		call = ' '.join(words) + r'\fR'
		result += heading(call, level=2)
		if 'description' in docs:
			result += fix_text(docs['description'])
		result += indent()
		if 'args' in docs:
			args = docs['args'] + '\n' # Extra \n simplifies the findargs regex somewhat.
			args = findargs.findall(args) # args is now a list of (arg, description)
			for arg, info in args:
				result += heading(italic(arg), level=2)
				if info[-1] != '.':
					info += '.'
				result += fix_text(info)
		if 'output' in docs:
			result += heading(bold('Output format string for quiet mode:'), level=2)
			result += escape_text(docs['output']) + '\n'
		if 'errors' in docs:
			result += heading(bold('Error cases with special return values:'), level=2)
			info = escape_text(docs['errors'])
			info = ' ' + info.replace('\n', '\n ') # Put a space at the start of each line. This makes nroff basically print it with whitespace verbatim
			info += '\n'
			result += info
		result += deindent()
	return result

if __name__=='__main__':
	import sys
	sys.stdout.write(man_page())
