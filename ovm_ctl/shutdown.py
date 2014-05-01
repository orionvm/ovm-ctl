from show import getvmby
from time import sleep
from sys import stdout

def shutdownvm(vmname, istty, api):
	"""call: 'shutdown vm VM'
	description: 'Stop running the given instance. While an instance is not running, no RAM usage charges are incurred.
	             .Note: Do not attempt to shut down your instance using the standard shut down feature of its operating system.
	             .Your instance will be restarted immediately and usage charges will continue.'
	args: 'VM: Name of the instance to stop running.'
	errors: 'VM name is invalid or VM does not exist: Return exit code 3
	        .VM not in a state to be shut down (eg. not running): Return exit code 4
	        .An error occurred while waiting for VM to shut down: Return exit code 5
	        .    Note: In this case, the VM may have not shut down correctly.
	        .    You should check with "show vm" and the out-of-band console ("console")
	        .    If the VM remains uncontactable and is still running after several minutes,
	        .    please contact OrionVM technical support.
	        .VM failed to shut down: Return exit code 6
	        .    This is a serious error. Plesae contact OrionVM technical support
	        .    and we will resolve the issue.'
	"""
	vm = getvmby(vmname, api, what='hostname')
	if vm is None:
		if istty:
			print vmname, "does not exist"
		return 3
	vmid = vm['vm_id']
	if vm['state'] != 2:
		if istty:
			print vmname, "is not in state to be shut down"
		return 4

	api.actionvm(vmid=vmid,action='shutdown')

	try:
		if istty:
			stdout.write("Shutting down...")
			stdout.flush()
		while 1:
			sleep(3)
			if istty:
				stdout.write('.')
				stdout.flush()
			vm = getvmby(vmname, api, what='hostname')
			if vm['state'] == 0:
				break
			if vm['state'] > 9:
				if istty:
					print "VM failed to shut down. Please contact OrionVM technical support and we will resolve the issue."
				return 6
	except:
		if istty:
			print "Error occurred while shutting down VM."
			print "Warning: VM may or may not have shut down correctly."
			print '         Please try "show vm %s" to check if VM has shut down.' % vmname
			print '         If VM has not shut down after several minutes'
			print '         and you cannot connect to the out of band console ("console %s"),' % vmname
			print '         we reccomend you contact OrionVM technical support'
			print '         and we will address the situation.'
		return 5

	if istty:
		print "Done"
	
