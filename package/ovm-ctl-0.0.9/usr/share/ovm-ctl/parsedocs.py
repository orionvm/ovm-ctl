
# All documentation (from which man page and help text is generated) is stored in the docstrins in each function.
# It consists of a number of fields of the following form:
#	"""FIELD: 'text
#	          .    All whitespace before the dot is ignored.'
#	"""

import re

def docs2dict(docstring):
	d = {}
	for match in re.finditer(r"(\w+): \s* ' ([^']*) '", docstring, re.X):
		field, value = match.groups()
		value = re.sub(r'\n[ \t]*([^. \t])', r' \1', value)
		value = re.sub(r'\n[ \t]*\.', r'\n', value)
		d[field] = value
	return d
