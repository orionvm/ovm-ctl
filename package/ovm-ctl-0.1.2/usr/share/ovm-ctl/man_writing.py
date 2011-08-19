"""Functions for formatting man pages"""
import time
import re

# This stuff is kinda nasty and specifically for writing man pages.
# Use it if you want but ovm-ctl itself never runs this file.

def title(name, section, date=None, source='', manual=''):
	"""Default date is current date. Set date to '' for no date. Should be YYYY-MM-DD
	source should be the origin of the command/function/subject.
	manual should be the title of the group of man pages (eg. 'Linux Programmers Manual')"""
	if date == None:
		year, month, day = time.localtime()[:3]
		date = '%04d-%02d-%02d' % (year, month, day)
	return '.TH %s %d %s %s %s\n' % (name, section, date, source, manual)

def heading(name, level=0):
	"""level between 0 and 2, 0 is more major"""
	if level == 0:
		request = 'SH '
	elif level == 1:
		request = 'SS '
	elif level == 2:
		request = 'TP\n'
	else:
		raise ValueError()
	return '.%s%s\n' % (request, name)

def multiheading(names):
	"""Makes a heading of level 2 with multiple lines (eg. a list of aliases).
	names is a non-empty list of strings."""
	if not names:
		raise ValueError()
	s = '.TP\n%s\n' % names[0]
	s += ''.join(['.TQ %s\n' % x for x in names[1:]])
	return s

def parbreak():
	"""Paragraph break"""
	return '.P\n'

def indent():
	return '.RS\n'

def deindent():
	return '.RE\n'

def itemize(bullet, items):
	"""As the LaTeX macro. Starts each item in items with bullet"""
	s = ''
	s += indent()
	for item in items:
		s += heading(bullet, 2) + item + '\n'
	s += deindent()
	return s

def code(text):
	"""Formats the text as code (fixed width, etc)"""
	return '.EX\n%s\n.EE\n' % text

def formatting(BorI, text, prefix='', suffix=''):
	"""BorI: 'B' for bold or 'I' for italic
	Concats prefix, text, suffix and makes text bold or italic"""
	if prefix:
		return '.R%s "%s" "%s" "%s"\n' % (BorI, prefix, text, suffix)
	if suffix:
		return '.%sR "%s" "%s"\n' % (BorI, text, suffix)
	return '.%s "%s"\n' % (BorI, text)

def bold(text, prefix='', suffix=''):
	return formatting('B', text, prefix, suffix)

def italic(text, prefix='', suffix=''):
	return formatting('I', text, prefix, suffix)

def begin_synopsis(name):
	return '.SY %s\n' % name

def option(opt, arg=''):
	"""Describes an optional argument in a command synopsis"""
	s = '.OP %s' % opt
	if arg:
		s += ' ' + arg
	s += '\n'
	return s

def end_synopsis():
	return '.YS\n'

def gen_synopsis(name, options=[], args=[], optional_args=[]):
	"""Generates a synopsis from options. Also puts args at the end.
	options: A list of ([shorts], [longs], arg, docstring) where:
		Each item is a distinct option - all options within one item are aliases
		arg is '' if no arg is needed, or else is the string that describes the arg.
		eg: (['f'], ['file'], 'filename') for a option -f or --file that takes an arg for a filename.
	args, optional_args is a list of argument descriptors"""
	result = begin_synopsis(name)
	shorts = []
	for s, l, a, doc in options: # Group non-arg shorts
		if not a:
			shorts += s
	result += option('-' + ''.join(shorts))
	for s, l, a, doc in options:
		aliases = []
		if a:
			aliases += ['-'+x for x in s]
		aliases += ['--'+x for x in l]
		if len(aliases) > 1:
			opt = '(%s)' % '|'.join(aliases)
		else:
			opt = aliases[0]
		result += option(opt, a)
	result += ''.join(['.I %s\n' % x for x in args])
	result += ''.join(['.RI [ %s ]\n' % x for x in optional_args])
	result += end_synopsis()
	return result

def check_result(s):
	"""Double-check a finished man page for blank lines (which break the formatting)
	Outputs a fixed copy where blank lines are now "blank requests" == "." """
	ret = ''
	for x in s.split('\n'):
		if not x:
			x = '.'
		ret += x + '\n'
	return ret

def fix_text(s):
	"""Takes a block of text and puts in newlines at the end of sentences. Also escapes backslashes."""
	s = escape_text(s)
	s = re.sub(r'\.(\s|$)', '.\n', s) # Put in newlines where needed
	s = re.sub(r'(^|\n)[ \t]+', r'\1', s) # Take out leading whitespace
	if s[-1] != '\n':
		s += '\n'
	return s

def escape_text(s):
	"""Escape any backslashes in text."""
	return s.replace('\\', '\\\\')
