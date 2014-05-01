import re
from webbindings import HTTPException

# Function to nicely format output into table columns if istty, otherwise tab separated
def printData(header, rows, istty):
    if header == None or not istty:
        allrows = rows
        if len(rows) == 0:
            return
    else:
        allrows = [header]
        allrows.extend(rows)
    
    width = len(allrows[0])
    
    if istty:
        # Find maximum width for each column among all rows
        padding = [0] * width
        for row in allrows:
            for x in range(len(row)):
            	if not isinstance(row[x], str):
            		row[x] = str(row[x])
                length = len(row[x])
                if length > padding[x]:
                    padding[x] = length
    
    # Tab separated for programmatic uses, nicely spaced for ttys
    for row in allrows:
        if istty:
            line = ""
            for x in range(width):
                line += row[x].ljust(padding[x] + 3)
            print line
        else:
            print "\t".join(map(str, row))

def showuse(istty, api): 
	r"""call: 'show usage'
	description: 'Report amount of RAM and HDD Storage being used,
		and the number of IP addresses currently allocated.'
	output: '"%d\t%d\t%d\n" ==> RAM in Megabytes, Storage in Gigabytes, Number of IPs'
	"""
	use = api.usage()
	if istty:
		if use['ram'] > 8*1024:
			use['ram'] /= 1024.0
			use['ram'] = ('%.2f' % use['ram']) + 'G'
		else:
			use['ram'] = str(use['ram']) + 'M'
		print "You are using %(ram)s of ram, %(disk)sG of disk, %(ip)s ips" % use
	else:
		print "%d\t%d\t%d" % (use['ram'], use['disk'], use['ip'])
	return 0

def showbalance(istty, api):
	r"""call: 'show balance'
	description: 'Report account balance, current to the last hour.'
	output: '"%.2f\n" ==> Balance in dollars (to the cent)'
	"""
	bal = api.details()['balance']
	if istty:
		print "Your account balance is $%.2f" % bal
	else:
		print "%.2f" % bal
	return 0

def showips(istty, api):
	r"""call: 'show ips'
	description: 'Print a list of IP addresses and their friendly names.'
	output: '"%s\t%s\n    ==>    IP Address, Friendly Name,
		. %s\t%s\n           IP Address, Friendly Name,
		. ..."               etc...(one per line)'
	"""
	ips = api.ip_pool()
	header = ['IP Address', 'Friendly Name']
	data = [[ip['ip'], ip['friendly']] for ip in ips]
	printData(header, data, istty)


def getvmby(value, api, what='vm_id'):
	"""Return the vm dict of the vm described in the arguments.
	The argument 'what' tells it what field to search on (default vmid).
	The argument 'value' is the expected value of the 'what' field you are searching for."""
	vms = api.vm_pool()
	for vm in vms:
		if vm[what] == value:
			return vm
	return None

def showip(matchip, istty, api):
	r"""call: 'show ip IP'
	description: 'Get information on a specific IP address, including up/down data totals,
		and (if in use) the vm using it.'
	args: 'IP: The IP address or friendly name to get information on.'
	output: '"%s\t%s\t%d\t%d\t%s\n" ==> IP Address, Friendly name,
		.                           Total Uploaded (bytes), Total Downloaded (bytes),
		.                           VM Name of VM using this IP (ommitted if not in use)'
	errors: 'For non-existing IP address or friendly name: Returns exit code 3'
	"""

	ips = api.ip_pool()
	for ip in ips:
		if ip['friendly'] == matchip or ip['ip'] == matchip:
			up = ip['up']
			down = ip['down']
			if istty:
				up, down = [x/float(1024**3) for x in (up, down)] # Convert to GB

			if ip['locked']:				
				vmname = getvmby(ip['vmid'], api, what='vm_id')['hostname']
				data = {'ip': ip['ip'], 'friendly': ip['friendly'], 'up': up, 'down': down, 'vmname': vmname}

				if istty:
					print "%(ip)s aka %(friendly)s %(up).2fG up/%(down).2fG down locked by %(vmname)s." % data
				else:
					print "%(ip)s\t%(friendly)s\t%(up)d\t%(down)d\t%(vmname)s" % data
			else:
				data = {'ip': ip['ip'], 'friendly': ip['friendly'], 'up': up, 'down': down}

				if istty:
					print "%(ip)s aka %(friendly)s %(up).2fGup/%(down).2fGdown is unlocked" % data
				else:
					print "%(ip)s\t%(friendly)s\t%(up)d\t%(down)d" % data
			break
	else:
		if istty:
			print "Cannot find ip", matchip
		return 3
	return 0

def showdisks(istty, api):
	r"""call: 'show disks'
	description: 'Print list of disks, their template image and their size.'
	output: '"%s\t%s\t%d\n    ==>    Disk Name, Image Name, Size (in GB)
		. %s\t%s\t%d\n           Disk Name, Image Name, Size (in GB)
		. ..."                   etc...(one per line)'
	"""
	disks = api.disk_pool()
	for disk in disks:
		if 'image' not in disk or not disk['image']:
			disk['image'] = '[blank]'
		disk['size'] = str(disk['size']) + ("G" if istty else "")

	header = ['Name', 'Image', 'Size']
	data = [  [ d['name'], d['image'], d['size'] ] for d in disks]
	printData(header, data, istty)

	return 0

def showdisk(diskname, istty, api):
	r"""call: 'show disk NAME'
	description: 'Get information on a specific disk, including image name, size and
	              whether the disk is locked (normally, attached to a vm)'
	args: 'NAME: The name of the disk to get information on.'
	output: '"%s\t%s\t%d\t%s\t%s\n" ==> Disk Name, Image Name, Size (in GB),
	        .                           "locked" if disk is locked, else "unlocked",
	        .                           licence if disk a licenced windows disk, else omitted'
	errors: 'Disk does not exist: Returns exit code 3'
	"""
	disks = api.disk_pool()
	for disk in disks:
		if disk['name'] == diskname:
			if 'image' not in disk or not disk['image']:
				disk['image'] = '[blank]'
			if istty:
				s = "%(name)s is of image %(image)s and size %(size)dG and %(islocked)s locked" % \
				{'name': disk['name'], 'image': disk['image'], 'size': disk['size'], 'islocked': ['is not', 'is'][disk['locked']]}
				if 'licence' in disk and disk['licence']:
					s += ' with licence %s' % disk['licence']
				print s
			else:
				print '\t'.join([disk['name'], disk['image'], str(disk['size'])] + (disk['locked'] and ['locked'] or ['unlocked']) + ('licence' in disk and disk['licence'] or []))
			break
	else:
		if istty:
			print 'Disk not found'
		return 3
	return 0
		
# Hi there. Reading through the source? Good for you!

def showvms(istty, api):
	r"""call: 'show vms'
	description: 'Print list of all vms, both running and shutdown.'
	output: '"%s\t%s\t%d\t%d\t%d\t%s\n    ==>    VM Name, VM Type, Memory (in MB), Number of disks, Number of ips, VM State
	        . %s\t%s\t%d\t%d\t%d\t%s\n           VM Name, VM Type, Memory (in MB), Number of disks, Number of ips, VM State
	        . ..."                               etc...(one per line)'
	"""
	vms = api.vm_pool()
	vmstates = {0: 'Shut down', 1: 'Booting', 2: 'Running', 3: 'Shutting down'}

	for vm in vms:
		if istty:
			if vm['ram'] >= 2048:
				vm['ram'] = "%.2fG" % (vm['ram'] / 1024.0)
			else:
				vm['ram'] = "%dM" % vm['ram']
		vm['state'] = vmstates.get(vm['state'], 'Erroring')

	
	header = ['Name', 'Type', 'Memory', 'Disks', 'IPs', 'State']
	data = [  [vm['hostname'], vm['vm_type'], vm['ram'], 
			  len(vm['disks']), len(vm['ips']), vm['state'] ] for vm in vms]
	
	printData(header, data, istty)
	
	return 0

def showvm(vmhost, istty, api):
	r"""call: 'show vm NAME'
	description: 'Get information on a specific VM, including running state,
	              attached disks and attached ips.'
	args: 'NAME: The name of the VM to get information on.'
	output: '"%s\t%s\t%d\t%s\n    ==>    VM Name, Type, Memory (in MB), State
	        . disk\t%s\t%s\t%s\n         Disk Name, Template, Device Name on VM
	        . disk\t%s\t%s\t%s\n         Disk Name, Template, Device Name on VM
	        . ...                        etc (one disk per line)
	        . ip\t%s\n                   IP Address
	        . ip\t%s\n                   IP Address
	        . ..."                       etc (one ip per line)'
	errors: 'For non-existing VM Name: Return exit code 3'
	"""
	# TODO when possible: Output list of context items
	vm = getvmby(vmhost, api, what='hostname')
	if vm is None:
		print "Cannot find vm", vmhost
		return 3

	vmstates = {0: 'Shut down', 1: 'Booting', 2: 'Running', 3: 'Shutting down'}
	if istty:
		if vm['ram'] >= 2048:
			ram = "%.2fG" % (vm['ram'] / 1024.0)
		else:
			ram = "%dM" % vm['ram']
		# Awful line. Wish print didn't behave so stupid. Wish python had a ?: ternary operator.
		print '%s of type %s has size %s and is currently %s' % (vm['hostname'], vm['vm_type'], ram, vmstates.get(vm['state'], "Erroring"))
	else:
		print '%s\t%s\t%d\t%s' % (vm['hostname'], vm['vm_type'], vm['ram'], vmstates.get(vm['state'], "Erroring"))
	for disk in vm['disks']:
		if 'image' not in disk or not disk['image']:
			disk['image'] = '[blank]'
		if istty:
			print "Contains disk %(name)s of image %(image)s as device %(target)s" % disk
		else:
			print "disk\t%(name)s\t%(image)s\t%(target)s" % disk
	
	if istty and vm['disks'] == []:
		print "Contains no disks"
	
	for ip in vm['ips']:
		print (istty and "Contains ip " or "ip\t") + ip

	if istty and vm['ips'] == []:
		print "Contains no ips"

	return 0

def get_ip(ip_str, api, istty):
	"""Convert a string into an ip address string. If already an address, no change. If is a valid friendly, replaces with the friendly's address. If doesn't match any friendly and not a valid address, returns ''"""
	
	ip_pool = api.ip_pool()
	for ip in ip_pool:
		if ip['friendly'] == ip_str:
			return ip['ip']
	parts = ip_str.split('.')
	if len(parts) != 4:
		return ''
	for part in parts:
		if not (0 <= int(part) < 256 and str(int(part)) == part):
			return ''
	return ip_str # is a valid ip

def showimages(istty, api):
	r"""call: 'show images'
	description: 'Get a list of available software distributions for creating new instances.
	             .Please note that the "blank" value is special, and is used to create a completely empty disk.'
	output: '"%s\n    ==>    Image
	        . %s\n           Image
	        . ..."           etc (one per line)'
	"""
	
	images = api.image_pool()

	for image in images:
		print image

def showcontext(key, vmname, istty, api):
	r"""call: 'show context key KEY on vm VM'
	description: 'Retrieve the value for the given key from the key-value context information associated with the given vm.'
	args: 'KEY: The context key to look up in the vm context store
	      .VM: The name of the vm to look up context information on'
	output: '"%s\n"    ==>    Value'
	errors: 'If the given vm does not exist, exit code 3 is returned.
	        .If the given vm context store does not contain the given key, exit code 4 is returned.'
	"""

	vm = getvmby(vmname, api, what='hostname')
	if not vm:
		if istty:
			print "VM %s does not exist" % vmname
		return 3

	try:
		value = api.get_context(vmid=vm['vm_id'],key=key)
	except HTTPException, e:
		if e.retcode != 404:
			raise
		if istty:
			print 'VM %s does not have context key %s' % (vmname, key)
		return 4

	if istty:
		print 'For vm %s:\t%s = %s' % (vmname, key, value)
	else:
		print value
