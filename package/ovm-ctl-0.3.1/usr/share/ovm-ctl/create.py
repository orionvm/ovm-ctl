import time
import sys
import re

def createdisk(diskname, size, image, isatty, api):
	""" call: 'create disk NAME with size SIZE [and image IMAGE]'
	description: 'Create a new storage volume and load it with the given software distribution.'
	args: 	'NAME: The name to give to the new disk.
	        .SIZE: The size of the new disk. Can be given in MB, GB or TB.
	        .      For example: "200G", "20g", "1.5T", "2048m". Value is rounded down to nearest GB.
	        .IMAGE: The software distribution to put onto the new disk. For a list of valid image names,
	        .        see the "show images" command. If not provided, creates a blank disk.'
	errors:	'If the given image is not valid, exit code 3 is returned.
	        .If the size is not valid, exit code 4 is returned.
	        .If there already exists a disk with name NAME, exit code 5 is returned.
	        .If an error occurs before creation is complete, exit code 6 is returned.
	        .    NOTE: The creation continues in the background, you must "show disks" to check
	        .    when it is done.'
	"""

	# If blank is given, this means no image
	if not image or image == 'blank':
		image = ""

	# Error check image name
	images = api.image_pool() + [""]
	if image not in images:
		if isatty:
			print '"%s" not a valid image. Please check against output of "show images".' % image
		return 3

	return _createdisk(diskname, size, image, isatty, api)

def _createdisk(diskname, size, image, isatty, api, minsize=1):
	"""Generic create disk function to be called by both 'create disk' and 'clone disk'
	Note that the return values honour both 'create disk' and 'clone disk' documentation."""

	# Check size variable and normalize to be in integer GB
	if not re.match(r'^(\d*\.)?\d+[GgTtMm]$', size):
		if isatty:
			print 'Not a valid size.'
		return 4
	size = size.upper()
	size = int( float(size[:-1]) * 1024.0 ** {'M':-1, 'G':0, 'T':1}[size[-1]] )
	if size < minsize:
		if isatty:
			print 'Size is too small. Disk must be at least %dG, not %dG.' % (minsize, size)
		return 4
	size = str(size) + 'G'

	# check disk doesn't already exist
	disks = api.disk_pool()
	names = [disk['name'] for disk in disks]
	if diskname in names:
		if isatty:
			print 'Cannot create disk "%s": A disk with that name already exists.' % diskname
		return 5

	if image:
		api.deploydisk(diskname=diskname, image=image, size=size)
	else:
		api.createdisk(diskname=diskname, size=size)

	try:
		if isatty:
			sys.stdout.write("Disk creating...")
			sys.stdout.flush()
	
		time.sleep(5)
		diskmade = False
		while not diskmade:
			if isatty:
				sys.stdout.write('.') # Illusion of progress so user doesn't think it's frozen
				sys.stdout.flush()
			disks = api.disk_pool()
			for disk in disks:
				if disk['name'] == diskname and disk['locked'] == False:
					diskmade = True
			time.sleep(5)
	except BaseException, e:
		if isatty:
			print e
			print '''Warning: Disk is still creating. Please check disk is fully created
         and listed in "show disks" before trying to use it.'''
		return 6
	else:
		if isatty:
			print "Created disk %s" % diskname


def clonedisk(diskname, source, size, isatty, api):
	"""call: 'clone disk NAME from SOURCE [with size SIZE]'
	description: 'Create a new disk called NAME, with contents copied from the disk called SOURCE.'
	args: 'NAME: The name of the new disk.
	      .SOURCE: The name of the disk to copy from. Must not be locked.
	      .SIZE: The size of the new disk (see the same arg for command "create disk").
	      .      Must be at least the size of the source disk.
	      .      If not provided, defaults to the size of the source disk.'
	errors:	'If the given source disk does not exist or is busy, exit code 3 is returned.
	        .If the size is too small or otherwise not valid, exit code 4 is returned.
	        .If there already exists a disk with name NAME, exit code 5 is returned.
	        .If an error occurs before creation is complete, exit code 6 is returned.
	        .    NOTE: The creation continues in the background, you must "show disks" to check
	        .    when it is done.'
	"""

	disk_pool = api.disk_pool()
	for disk in disk_pool:
		if disk['name'] == source:
			source_disk = disk
			if disk['locked']:
				if isatty:
					print 'Cannot clone from disk "%s": Disk is locked. Maybe you need to detach it first?' % source
				return 3
			break
	else:
		if isatty:
			print 'Source disk "%s" does not exist.' % source
		return 3

	if not size:
		size = str(source_disk['size'])+'G'

	return _createdisk(diskname, size, source, isatty, api, minsize=source_disk['size'])


def createip(friendly, isatty, api):
	"""call: 'create ip with friendly NAME'
	description: 'Allocate a new IP address and call it NAME.'
	args: 'NAME: The friendly name to assign to the new address.'
	"""
	ip = api.allocateip(friendly=friendly) # If only all the bindings were this simple...

	if isatty:
		print "Ip", ip['ip'], "allocated"
	

def createvm(hostname, ram, type, istty, api):
	"""call: 'create vm NAME with ram SIZE [of type TYPE]'
	description: 'Create a new VM and call it NAME. Give it SIZE amount of memory.
	             .Optionally, a VM Type can be provided. This is for advanced use only.'
	args: 'NAME: The name to give to the new VM.
	      .SIZE: Amount of RAM to allocate to the new VM.
	      .      Format is a number followed by M for megabytes or G for gigabytes.
	      .TYPE: Either "paravirt" or "HVM". Note that not all distros support all types.
	      .      "HVM" should be used when creating Microsoft Windows VMs. "paravirt" should
	      .      otherwise be used and is the default if this argument is not given.'
	errors: 'Incorrect format for SIZE: Return exit code 3
	        .Invalid VM Type: Return exit code 4'
	"""

	ram = ram.upper()
	if not re.match('[1-9][0-9]*(G|M)', ram):
		if istty:
			print 'Bad format for ram size: Must be a number followed by "M" for megabytes or "G" for gigabytes.'
		return 3

	if type:
		if type not in ('paravirt', 'HVM'):
			if istty:
				print 'Invalid type "%s": Must be "paravirt" or "HVM"' % type
			return 4
	else:
		type = 'paravirt'

	vmid = api.allocatevm(hostname=hostname, ram=ram, vm_type=type)

	if vmid > 0:
		if istty:
			print "Successfully created VM %s" % hostname
	else:
		raise Exception("allocatevm returned 0") # This will be caught and "unknown error" presented.
