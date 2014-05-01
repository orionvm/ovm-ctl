from show import getvmby
from webbindings import HTTPException
import re

def setram(vmname, ram, istty, api):
	"""call: 'set ram on vm NAME to SIZE'
	description: 'Update the ram of a VM. VM Must be stopped.'
	args: 'NAME: The name of the VM.
	      .SIZE: Amount of RAM to set on the VM.
	      .      Format is a number followed by M for megabytes or G for gigabytes.
	      .		 Value must be between 512M and 64G (65536M)
	errors: 'VM name is invalid or VM does not exist: Return exit code 3
	        .Incorrect format for SIZE: Return exit code 5'
	"""
	vm = getvmby(vmname, api, what='hostname')
	if not vm:
		if istty:
			print 'VM %s does not exist' % vmname
		return 3

	if vm['state'] != 0:
		if istty:
			print vmname, " is not in a state to have ram changed"
		return 4

	ram = ram.upper()
	if not re.match('^(((\d*[.])?\d+G)|([1-9][0-9]+M))$', ram):
		if istty:
			print 'Bad format for ram size: Must be a number followed by "M" for megabytes or "G" for gigabytes.'
		return 5

	unit = ram[-1]
	ram = float(ram[0:-1])
	if unit == "G":
		ram = int(ram * 1024)
		
	if ram < 512 or ram > 65536:
		if istty:
			print 'RAM must be between 512M and 64G (65536M)'
		return 5	
		
	ram = "%sM" % ram

	api.set_ram(vmid=vm['vm_id'], ram=ram)