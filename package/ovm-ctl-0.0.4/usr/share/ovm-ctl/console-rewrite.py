raise Exception("This module is not in a fit state to run. If you're running this, you need to fix your version.")
# This version is a half-done rewrite of console.py
# Some of the changes have been written back into the proper console.py but it still has the outstanding password issue.

import os, sys
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile as tmpfile

def runconsole(vmname, istty, api):

	console_ip = '49.156.16.12'
	console_rsa = "%s ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA1ZKuRj8UkoCUvGKGSGd9vQAlP3uCmq+8vBdF/SeZ2sr0Gf9+ZTn5Di8EGBBwOArU791VTtTWTg2kSC6xbearWH9xxD8omnjaYyBmqBLZ0yimVuIQWh3QS5YglxdQoGZUJ7a7ddQDLvO11f4eirP6HcNYSfGT5070jqoEiETmdcoQsdsxdJFs6GBssMoMij1i4HRDbCDPMdViEOQ19LQBCd3LsTFcmZJ/LIO9BCxsSeyV5IPkUVVzVc29JOmqDbCTcHuOidrupVheSSkZjhB0Cq6L8tOaFP/5gj7Ab6PiZPC3hOoLFgPJ3zk50RfAT2/enKqwHQFnN1QzfBBMg1kJiw==" % console_ip

	# Check vmname exists. This also checks user/pswd is valid.

	# Write a temporary known hosts file, which means we don't clutter up user's ~/.ssh/known_hosts:
	hostfile = tmpfile()
	hostfile.write(console_rsa)
	hostfile.flush()

	try:
		proc = Popen(['ssh', '-qqt', '-oGlobalKnownHostsFile=%s' % hostfile.name, 'console@%s' % console_ip, "%s %s  " % (api.user, vmname)], stdin=PIPE, stdout=PIPE) # Extra two spaces are a workaround for a console-side error.
	except OSError:
		if istty:
			print 'Failed to start remote shell. Is the program "ssh" installed and accessbile?'
		return 3

	proc.stdin.write(api.pswd + '\n')
	# Eat first two lines, which are a greeting and a password prompt.
	proc.stdout.readline()
	proc.stdout.readline()

	os.dup2(sys.stdin.fileno(), proc.stdin.fileno()) # Overwrite the proc PIPE fd with stdin
