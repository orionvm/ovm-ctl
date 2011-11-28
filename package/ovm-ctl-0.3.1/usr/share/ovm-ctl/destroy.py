import time, sys
from show import getvmby, get_ip


def destroyip(ipname, istty, api):
	"""call: 'destroy ip IP'
	description: 'Unallocate the given IP, which must not be locked (in use by a VM).
	             .Once an IP has been unallocated, there is no guarentee
	             .you can get the same one back again.
	             .Note that unlocked IPs still incur a charge until they have been destroyed.'
	args: 'IP: The IP address or friendly name to unallocate.'
	errors: 'IP is invalid, or no matching friendly name found: Returns exit code 3'
	"""
	ip = get_ip(ipname, api, istty)
	if not ip:
		if istty:
			print '%s not a valid address and no matching friendly name found' % ipname
		return 3

	api.dropip(ip=ip)

	if istty:
		print "Destroyed ip %s" % ipname
	

def destroydisk(diskname, istty, api):
	"""call: 'destroy disk DISK'
	description: 'Destroys the given disk that is not locked (attached to a VM).
	             .All data on the disk is lost. OrionVM is not responsible for any data lost this way.
	             .Please be very careful when dealing with unlocked disks.'
	args: 'DISK: Name of the disk to destroy.'
	errors: 'An error occurs while waiting for disk to be destroyed: Returns exit code 3
	        .    NOTE: When this occurs, the disk may or may not be destroyed.
	        .    Please run "show disks" and check if the disk is on the list.'
	"""

	api.dropdisk(diskname=diskname)

	time.sleep(1)

	if istty:
		sys.stdout.write("Dropping disk...")
		sys.stdout.flush()
	try:
		diskexists = True
		while diskexists:
			diskexists = False

			disks = api.disk_pool()
			for disk in disks:
				if disk['name'] == diskname:
					diskexists = True
					time.sleep(1)
					if istty:
						sys.stdout.write('.')
						sys.stdout.flush()
					continue
	except:
		if istty:
			print "An error occurred while dropping disk"
			print 'Please try "show disks" to check if your disk was successfully dropped'
		return 3

	if istty:
		print "Done"

def destroyvm(vmname, istty, api):
	"""call: 'destroy vm VM'
	description: 'Destroy given non-running instance.
	             .Note that any attached disks or IPs will still exist and continue to incur charges.'
	args: 'VM: Name of the instance to delete.'
	errors: 'VM does not exist: Return exit code 3'
	"""
	vm = getvmby(vmname, api, what='hostname')	
	if vm is None:
		print "VM does not exist"
		return 3

	vmid = vm['vm_id']

	api.dropvm(vmid=vmid)

	if istty:
		print "Destroyed vm %s" % vmname
