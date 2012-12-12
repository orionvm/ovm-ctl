from show import getvmby, get_ip

def detachdisk(diskname, vmname, istty, api):
	"""call: 'detach disk DISK from VM'
	description: 'Detach the given disk from the instance its attached to, removing it from that system but freeing it to be destroyed or attached elsewhere.'
	args: 'DISK: Name of the disk to detach.
	      .VM: Name of the instance that the disk is currently attached to.'
	errors: 'VM does not exist or is not shut down: Returns exit code 3
	        .Disk not attached to VM, or disk does not exist: Returns exit code 4'
	"""

	vm = getvmby(vmname, api, what='hostname')
	if vm is None:
		if istty:
			print "VM %s does not exist" % vmname
		return 3
	if vm['state'] != 0:
		if istty:
			print "VM %s is not shut down" % vmname
		return 3

	found = False
	for disk in vm['disks']:
		if disk['name'] == diskname:
			found = True
	if not found:
		if istty:
			print "Disk %s not attached to VM %s" % (diskname, vmname)
		return 4

	vmid = vm['vm_id']
	api.detachdisk(vmid=vmid, diskname=diskname)

	if istty:
		print "Detached %s from %s" % (diskname, vmname)

def detachip(ipname, vmname, istty, api):
	"""call: 'detach ip IP from VM'
	description: 'Detach the given IP from the instance its attached to, allowing it to be freed or attached to a different instance instead.'
	args: 'IP: The IP address or friendly name you want to detach.
	      .VM: The name of the instance that the ip is currently attached to.'
	errors: 'VM does not exist: Returns exit code 3
	        .Invalid IP or no matching friendly IP name found: Returns exit code 4'
	"""
	vm = getvmby(vmname, api, what='hostname')
	if vm is None:
		if istty:
			print "VM %s does not exist" % vmname
		return 3

	# look up ip by friendly name
	ip = get_ip(ipname, api, istty)
	if not ip:
		if istty:
			print 'IP address invalid, or no matching friendly name found.'
		return 4
	
	vmid = vm['vm_id']
	api.detachip(ip=ip, vmid=vmid)

	if istty:
		print "Detached %s from %s" % (ipname, vmname)
