#!/usr/bin/env python
import urllib2
import httplib
import ssl
import socket
import os
import re

CA_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'ca.pem')

class CertificateError(Exception):
    pass

# The following 2 functions are from Python 3 lib/ssl
# To bring SSL hostname matching to Python 2
def ssl_dnsname_match(dn, hostname, max_wildcards=1):
	"""Matching according to RFC 6125, section 6.4.3

	http://tools.ietf.org/html/rfc6125#section-6.4.3
	"""
	pats = []
	if not dn:
		return False

	parts = dn.split(r'.')
	leftmost = parts[0]
	remainder = parts[1:]

	wildcards = leftmost.count('*')
	if wildcards > max_wildcards:
		# Issue #17980: avoid denials of service by refusing more
		# than one wildcard per fragment.  A survery of established
		# policy among SSL implementations showed it to be a
		# reasonable choice.
		raise CertificateError(
			"too many wildcards in certificate DNS name: " + repr(dn))

	# speed up common case w/o wildcards
	if not wildcards:
		return dn.lower() == hostname.lower()

	# RFC 6125, section 6.4.3, subitem 1.
	# The client SHOULD NOT attempt to match a presented identifier in which
	# the wildcard character comprises a label other than the left-most label.
	if leftmost == '*':
		# When '*' is a fragment by itself, it matches a non-empty dotless
		# fragment.
		pats.append('[^.]+')
	elif leftmost.startswith('xn--') or hostname.startswith('xn--'):
		# RFC 6125, section 6.4.3, subitem 3.
		# The client SHOULD NOT attempt to match a presented identifier
		# where the wildcard character is embedded within an A-label or
		# U-label of an internationalized domain name.
		pats.append(re.escape(leftmost))
	else:
		# Otherwise, '*' matches any dotless string, e.g. www*
		pats.append(re.escape(leftmost).replace(r'\*', '[^.]*'))

	# add the remaining fragments, ignore any wildcards
	for frag in remainder:
		pats.append(re.escape(frag))

	pat = re.compile(r'\A' + r'\.'.join(pats) + r'\Z', re.IGNORECASE)
	return pat.match(hostname)

def ssl_match_hostname(cert, hostname):
	"""Verify that *cert* (in decoded format as returned by
	SSLSocket.getpeercert()) matches the *hostname*.  RFC 2818 and RFC 6125
	rules are followed, but IP addresses are not accepted for *hostname*.

	CertificateError is raised on failure. On success, the function
	returns nothing.
	"""
	if not cert:
		raise ValueError("empty or no certificate")
	dnsnames = []
	san = cert.get('subjectAltName', ())
	for key, value in san:
		if key == 'DNS':
			if ssl_dnsname_match(value, hostname):
				return
			dnsnames.append(value)
	if not dnsnames:
		# The subject is only checked when there is no dNSName entry
		# in subjectAltName
		for sub in cert.get('subject', ()):
			for key, value in sub:
				# XXX according to RFC 2818, the most specific Common Name
				# must be used.
				if key == 'commonName':
					if ssl_dnsname_match(value, hostname):
						return
					dnsnames.append(value)
	if len(dnsnames) > 1:
		raise CertificateError("hostname %r "
			"doesn't match either of %s"
			% (hostname, ', '.join(map(repr, dnsnames))))
	elif len(dnsnames) == 1:
		raise CertificateError("hostname %r "
			"doesn't match %r"
			% (hostname, dnsnames[0]))
	else:
		raise CertificateError("no appropriate commonName or "
			"subjectAltName fields were found")

# http://stackoverflow.com/questions/6648952/urllib-and-validation-of-server-certificate
class ValidHTTPSConnection(httplib.HTTPConnection):
	"This class allows communication via SSL."

	default_port = httplib.HTTPS_PORT

	def __init__(self, *args, **kwargs):
		httplib.HTTPConnection.__init__(self, *args, **kwargs)

	def connect(self):
		"Connect to a host on a given (SSL) port."
		
		self.sock = socket.create_connection( (self.host, self.port),
		    self.timeout, self.source_address)
            
		if self._tunnel_host:
			self._tunnel()
			
		global CA_FILE
		self.sock = ssl.wrap_socket(self.sock,
			ca_certs=CA_FILE, cert_reqs=ssl.CERT_REQUIRED)
	
		cert = self.sock.getpeercert()
		ssl_match_hostname(cert, self.host)


class ValidHTTPSHandler(urllib2.HTTPSHandler):

	def https_open(self, req):
			return self.do_open(ValidHTTPSConnection, req)
