import show, attach, create
from boot import bootvm
from password import setpass
from context import addcontext
from time import sleep

def vmwizard(name, memsize, disksize, image, boot, isatty, api):
	"""call: 'wizard vm NAME [with [ram MEMSIZE] [disk DISKSIZE] [image IMAGE]] [and boot]'
	description: 'This command is a wizard to create a ready-to-run server with the given NAME.
	             .Any arguments not provided will be prompted. If the command has "and boot" on the end,
	             .the machine will be booted immediately after creation.
	             .Further details:
	             .    Create a new VM and call it NAME. Create a disk and ip (of the same NAME) and attach them.
	             .    The disk will have size DISKSIZE and image IMAGE. The VM will have ram MEMSIZE.
	             .    If "and boot" is given, the VM is then booted.
	             .    If "and boot" is not given, it is only prompted if no other arguments are provided.'
	args: 'NAME: The name to give to the VM, disk and ip address to be created.
	      .MEMSIZE: The amount of RAM to give the VM.
	      .         Format is a number followed by M for megabytes or G for gigabytes.
	      .DISKSIZE: The size of the new disk. See the SIZE argument for "create disk".'
	output: 'If creating a windows vm, prints the inital password'
	errors: 'NOTE: In the event of any sort of error, the VM may have only been partially constructed.
	        .      Please use the show commands and check what has and has not been created.
	        .Not all arguments provided and in quiet mode: Return exit code 1 (invalid command)
	        .Incorrect format for MEMSIZE: Return exit code 3
	        .Incorrect format for DISKSIZE: Return exit code 4
	        .Invalid value for IMAGE: Return exit code 5
	        .Already a disk, ip or VM called NAME: Return exit code 6
	        .An error occurred in booting the VM: Return exit code 7
	        .    Note: This means that the VM was successfully created.
	        .    Failure to boot means it is now in a Shut Down state.
	        .Any other error occurred during the operation: Return exit code 8
"""
	boot = boot == " and boot"

	# Get inputs
	if not isatty and not (memsize and disksize and image):
		return 1
	askboot = not (memsize or disksize or image or boot)
	if not memsize:
		memsize = raw_input("How much RAM? ")
	if not disksize:
		disksize = raw_input("How much disk space? ")
	if not image:
		show.showimages(isatty, api)
		image = raw_input("Please select one of the images above: ")
	if askboot:
		boot = raw_input("Would you like to boot the VM immediately? (y/n) > ") == "y"

	if show.getvmby(name, api, what='hostname'):
		if isatty:
			print "A VM with that name already exists."
		return 6

	type = ['paravirt', 'HVM']['windows' in image]
	ret = create.createvm(name, memsize, type, isatty, api)
	if ret == 3:
		return 3
	if ret:
		raise Exception("Unknown return value from createvm: %d"%ret)

	ret = create.createdisk(name, disksize, image, isatty, api)
	if ret == 3:
		return 5
	if ret == 4:
		return 4
	if ret == 5:
		return 6
	if ret == 6:
		return 8
	if ret:
		raise Exception("Unknown return value from createdisk: %d"%ret)

	ret = attach.attachdisk(name, name, ('windows' in image) and "hda" or "xvda1", isatty, api)
	if ret:
		raise Exception("Unexpected return value from attachdisk: %d"%ret)

	ret = create.createip(name, isatty, api)
	if ret:
		raise Exception("Unknown return value from createip: %d"%ret)

	ret = attach.attachip(name, name, isatty, api)
	if ret:
		raise Exception("Unknown return value from attachip: %d"%ret)

	if 'windows' in image:
		addcontext(name, 'WINDOWS', 'true', isatty, api)
		setpass(name, '', isatty, api)

	if boot:
		ret = bootvm(name, isatty, api)
		if ret == 5:
			return 7
		if ret == 6:
			return 8
		if ret:
			raise Exception("Unexpected return value from bootvm: %d"%ret)
