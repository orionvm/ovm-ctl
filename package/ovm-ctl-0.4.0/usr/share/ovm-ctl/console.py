import os
from subprocess import Popen
from tempfile import NamedTemporaryFile as tmpfile
from show import getvmby

# TODO A few things about this need a rewrite.
# Being able to see password on process list, big issue on multi-user systems.
# An attempted (unfinished) rewrite can be found in console-rewrite.py,
# but I think it'll have to wait until the console server behaviour changes.

def runconsole(vmname, istty, api):
	"""call: 'console VM'
	description: 'Log into the out-of-band management console on the given instance.
	             .This is roughly equivilent to directly connecting to the serial port on the machine.
	             .This command requires the programs "grep" and "ssh" be installed
	             .and accessible in a folder listed in the PATH environment variable.
	             .See NOTES section of the man page for extra notes.'
	args: 'VM: The instance to connect to.'
	errors: 'VM does not exist: Return exit code 3
	        .Fail to run ssh: Return exit code 4
	        .ssh exits with non-zero code (generic error): Return exit code 5
	        .ssh exits with code 255 (connection or protocol error): Return exit code 6'
	"""

	console_ip = '49.156.16.12' # IP of OVM console server
	console_rsa = "%s ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA1ZKuRj8UkoCUvGKGSGd9vQAlP3uCmq+8vBdF/SeZ2sr0Gf9+ZTn5Di8EGBBwOArU791VTtTWTg2kSC6xbearWH9xxD8omnjaYyBmqBLZ0yimVuIQWh3QS5YglxdQoGZUJ7a7ddQDLvO11f4eirP6HcNYSfGT5070jqoEiETmdcoQsdsxdJFs6GBssMoMij1i4HRDbCDPMdViEOQ19LQBCd3LsTFcmZJ/LIO9BCxsSeyV5IPkUVVzVc29JOmqDbCTcHuOidrupVheSSkZjhB0Cq6L8tOaFP/5gj7Ab6PiZPC3hOoLFgPJ3zk50RfAT2/enKqwHQFnN1QzfBBMg1kJiw==" % console_ip
	
	# Check vmname exists. This also checks user/pswd is valid.
	if not getvmby(vmname, api, what='hostname'):
		if istty:
			print 'Cannot find vm "%s"' % vmname
		return 3
	
	# Write a temporary known hosts file, which means we don't clutter up user's ~/.ssh/known_hosts:
	hostfile = tmpfile()
	hostfile.write(console_rsa)
	hostfile.flush()

	try:
		proc = Popen(['ssh', '-qqt', '-oGlobalKnownHostsFile=%s' % hostfile.name, 'console@%s' % console_ip, "%s %s %s" % (api.user, vmname, api.pswd)])
	except OSError:
		if istty:
			print 'Failed to start remote shell. Is the program "ssh" installed and accessbile?'
		return 4

	ret = proc.wait()
	if ret:
		if istty:
			print 'Remote shell failed with exit code %d' % ret
		if ret == 255:
			return 6
		else:
			return 5
