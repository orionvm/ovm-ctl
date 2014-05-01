import base64
import time
import urllib
import urllib2
import sys
import re

try:
    import simplejson as json
except ImportError:
    import json

from sslverify import ValidHTTPSHandler

from ovm_ctl import __version__ as VERSION

# This file contains the web api object itself, without all the fancy wrapping.
# If you want to use this for your python program, just create a apibindings object.
# This object contains all the calls - if you look at the calls list in __init__,
# 	the 2nd thing in each tuple is the python member name for that function.
# Example:
# >>> api = apibindings('example', 'passw0rd')
# >>> print api.disk_pool()
#
# IMPORTANT: Our actual API is not finalised yet,
# so if you use these be aware they may completely change some day with no warning.

class HTTPException(Exception):
	def __init__(self, message, retcode, response=None):
		Exception.__init__(self, message)
		self.retcode = retcode
		self.response = response

   
class MethodAndCredsRequest(urllib2.Request):
	def __init__(self, method, user, pswd, *args, **kwargs):
		self._method = method
		if 'headers' not in kwargs: kwargs['headers'] = {}
		kwargs['headers']['User-Agent'] = "OrionVM CLI bindings version %s" % VERSION
		if user and pswd:
			basicheader = "Basic " + base64.b64encode(user + ":" + pswd)
			kwargs['headers']['Authorization'] = basicheader
		urllib2.Request.__init__(self, *args, **kwargs)

	def get_method(self):
		return self._method if self._method else super(RequestWithMethod, self).get_method()


def push(url, post_data, user, pswd, verbose=False, type='GET', con=None, retcon=False):
	opener = con
	
	if verbose:
		print url, post_data

	data = None

	#string_s = StringIO.StringIO()
	#header_s = StringIO.StringIO()

	if post_data and type=='POST':
		data = urllib.urlencode(post_data)
	else:
		if post_data:
			url += '?' + '&'.join(['%s=%s' % (k,v) for k,v in post_data.items()])
		
	if not opener:		
		opener = urllib2.OpenerDirector()
		opener.add_handler(ValidHTTPSHandler())
		opener.add_handler(urllib2.HTTPDefaultErrorHandler())
		opener.add_handler(urllib2.HTTPErrorProcessor())

	req = MethodAndCredsRequest(type, user, pswd, url, data)
	try:
		response = opener.open(req)
	except urllib2.URLError, e:
		if not hasattr(e, 'code'):
			raise
		retcode = e.code
		page = e.read()
	else:
		retcode = 200
		page = response.read()
	
	if retcode != 200:
		raise HTTPException("API error %s" % retcode, retcode, response=page)

	if not retcon:
		return page

	return page, opener

def extra(isatty, api):
	if not isatty:
		print 'No moo\tDo have OVM power\tRun with -v'
		return 0
	enc = open('extra', 'r').read()
	enc = enc.split('\n')
	partial = [''] * len(enc[0])
	for x in range(len(enc[0])):
		for line in enc:
			partial[x] += line[x]
	dec = base64.decodestring('\n'.join(partial))
	print 'Sorry, no Super Cow Powers here.'
	time.sleep(1)
	print 'But we do have Super OrionVM Powers!'
	time.sleep(2)
	sys.stdout.write("You don't believe me")
	sys.stdout.flush()
	time.sleep(2)
	for msg in ['.', '.', '.', '?']:
		sys.stdout.write(msg)
		sys.stdout.flush()
		time.sleep(1)
	time.sleep(2)
	print dec
extra_r = [('', r'^(?:show|create|destroy|attach|detach) moo$', extra)]

class apibindings(object):
	def __init__(self, user, pswd):
		self.GET = 'GET'
		self.POST = 'POST'
		self.user = user
		self.pswd = pswd

		base = "https://panel.orionvm.com.au/api/"
		# list of (api url, binding name, method)
		calls = [(r'vm_pool', 'vm_pool', self.GET),
			(r'ip_pool', 'ip_pool', self.GET),
			(r'disk_pool', 'disk_pool', self.GET),
			(r'image_pool', 'image_pool', self.GET),
			(r'user_details', 'details', self.GET),
			(r'deploy_disk', 'deploydisk', self.POST),
			(r'create_disk', 'createdisk', self.POST),
			(r'allocate_ip', 'allocateip', self.POST),
			(r'vm_allocate', 'allocatevm', self.POST),
			(r'attach_disk', 'attachdisk', self.POST),
			(r'attach_ip', 'attachip', self.POST),
			(r'detach_disk', 'detachdisk', self.POST),
			(r'detach_ip', 'detachip', self.POST),
			(r'deploy', 'deploy', self.POST),
			(r'action', 'actionvm', self.POST),
			(r'drop_ip', 'dropip', self.POST),
			(r'drop_disk', 'dropdisk', self.POST),
			(r'drop_vm', 'dropvm', self.POST),
			(r'usage', 'usage', self.GET),
			(r'context', 'get_context', self.GET),
			(r'context', 'set_context', self.POST),
			(r'set_ram', 'set_ram', self.POST)]

		self.con = None
		for url, nme, type in calls:
			newfunc = self._docall(base + url, type)
			self.__dict__[nme] = newfunc


	def _docall(self, url, type):
		def fun(**kwargs):
			ret, self.con = push(url, kwargs, self.user, self.pswd, verbose=False, type=type, con=self.con, retcon=True)
			return json.loads(ret)

		return fun

# deprecated
def protectAPI(call, istty, *args, **kwargs):
	"""Wrap every api call with common error handling
	***DEPRECATED*** in favour of more general error handling higher up in the call stack."""
	try:
		return call(*args, **kwargs)
	except HTTPException, e:
		if istty:
			print 'Error while calling API function %s: Returned code %d' % (call.__name__, e.retcode)
			if e.response:
				if raw_input('View entire web response? (y/n) > ') == 'y':
					print e.response
		raise
