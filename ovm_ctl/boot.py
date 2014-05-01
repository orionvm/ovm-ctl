from show import getvmby
from time import sleep
from sys import stdout

def bootvm(vmname, istty, api):
	"""call: 'boot vm VM'
	description: 'Begin running the given instance.'
	args: 'VM: Name of the instance to boot up.'
	errors: 'If VM name is invalid or VM does not exist: Returns exit code 3
	        .If VM is not ready to be booted (eg. is already running): Returns exit code 4
	        .If VM fails to correctly boot (booting is aborted): Returns exit code 5
	        .If an error occurs while booting: Returns exit code 6
	        .    NOTE: In this case, the VM may still boot correctly.
	        .    Try "show vm" to check if the VM is now running or still booting.'
"""
	vm = getvmby(vmname, api, what='hostname')
	if vm is None:
		if istty:
			print vmname, "does not exist"
		return 3
	vmid = vm['vm_id']
	if vm['state'] != 0:
		if istty:
			print vmname, "is not in state to be booted"
		return 4

	api.deploy(vmid=vmid)

	if istty:
		stdout.write('Booting.')
		stdout.flush()
	try:
		while 1:
			sleep(3)
			if istty:
				stdout.write('.') # Give the user some feedback that it isn't frozen
				stdout.flush()
			vm = getvmby(vmname, api, what='hostname')
			if vm['state'] not in (1,2):
				if istty:
					print "Failed to boot"
				return 5
			if vm['state'] == 2:
				break
	except:
		if istty:
			print 'Unknown error while waiting for VM to boot.'
			print 'Warning: VM is not booted. However, it is still booting.'
			print '         Please use "show vm %s" to check if VM successfully booted.' % vmname
		return 6

	if istty:
		print "Done"

