import random
from context import addcontext


def setpass(vmname, password, istty, api):
	"""call: 'set password on vm VM[ to PASSWORD]'
	description: 'On next boot, vm will have password set to the given password.
	             .Note that this requires we store the password in our system, in plaintext.
	             .As such you may wish to instead use a temporary password here then change it manually.
	             .To this end, a random password is chosen if none is provided.'
	output: '"%s\n"   ->   New password'
	args: 'VM: The vm to set the password of. Note that while a change may be made while the vm is running,
	      .    changes will not take effect until the next boot.
	      .PASSWORD: Optional. The new password to set. May contain whitespace.
	      .    If not given, a random 8 character password is generated.'
	errors: 'If the VM does not exist: Return exit code 3'
	"""
	if not password:
		password = genrandom()
	ret = addcontext(vmname, 'PASSWORD', password, istty, api)
	if ret:
		return ret
	if istty:
		print 'Set password to "%s"' % password
	else:
		print password
	return 0

def genrandom():
	alphabet = [chr(x) for x in range(ord('0'),ord('~'))]
	return ''.join(random.sample(alphabet, 8))
