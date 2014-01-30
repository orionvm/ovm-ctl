from show import getvmby
import re
from webbindings import HTTPException

def attachdisk(diskname, vmname, target, istty, api):
	r"""call: 'attach disk DISK to VM with target TARGET'
	    description: 'Attach a given disk to a given VM, locking the disk
	                 .and making it appear as a device on the VM.'
	    args: 'DISK: The name of the disk to attach.
	          .VM: The name of the VM to attach to.
	          .TARGET: The name of the device (the device will appear as /dev/TARGET).
	          .        For a linux vm:
	          .            Must be of form: "xvd%s%d" ==> ((a, b, c, ..., aa, ab, etc), positive integer),
	          .            eg: "xvda1", "xvda2", "xvdb1", "xvdb25".
	          .            Note: "xvdz" is reserved. Valid range is "xvda"-"xvdy", then "xvdaa", etc.
	          .        For a windows vm:
	          .            Must be of form: "hd%s" ==> (a, b, c, ..., aa, ab, ...)
	          .            eg. "hda", "hdb", "hdog", "hdzzz"'
	    errors: 'For non-existing or invalid (eg. running) VM: Returns exit code 3
	            .For non-existing or invalid Disk: Returns exit code 4
	            .For invalid target: Returns exit code 5'
    """
	print diskname, vmname, target
	vm = getvmby(vmname, api, what='hostname')
	if vm is None:
		if istty:
			print "VM %s does not exist" % vmname
		return 3
	if vm['state'] != 0:
		if istty:
			print "VM %s is not currently shut down" % vmname
		return 3

	if not diskname in [disk['name'] for disk in api.disk_pool()]:
		if istty:
			print "Disk %s does not exist" % diskname
		return 4

	# Note xvdz is reserved for context store access / future use
	if (target.startswith('xvdz') or not re.match('xvd[a-z]+[1-9][0-9]*', target)) and not re.match('hd[a-z]+', target):
		if istty:
			print "Target %s is not valid" % target
		return 5

	vmid = vm['vm_id']
	api.attachdisk(vmid=vmid, diskname=diskname, target=target, readonly=False)
	if istty:
		print "Attached %s to %s" % (diskname, vmname)

def attachip(ipname, vmname, istty, api):
        r"""call: 'attach ip IP to vm VM'
        description: 'Attach a given IP to a given VM,
	             .creating an ethernet interface on the VM.'
        args: 'IP: The IP Address or Friendly Name of the IP to attach.
	      .VM: The name of the VM to attach it to.'
        errors: 'For non-existing or invalid VM: Return exit code 3
	        .For non-existing or invalid IP: Return exit code 4'
        """
	vm = getvmby(vmname, api, what='hostname')
	if vm is None:
		if istty:
			print "VM %s does not exist" % vmname
		return 3

	ipaddr = None
	ip_pool = api.ip_pool()
	for ip in ip_pool:
		if ip['ip'] == ipname:
			ipaddr = ip['ip']
	if not ipaddr:
		for ip in ip_pool:
			if ip['friendly'] == ipname:
				ipaddr = ip['ip']
	if not ipaddr:
		if istty:
			print "IP %s does not exist" % ipname
		return 4
	
	vmid = vm['vm_id']
	api.attachip(ip=ipaddr, vmid=vmid)

	if istty:
		print "Attached ip %s to %s" % (ipname, vmname)
