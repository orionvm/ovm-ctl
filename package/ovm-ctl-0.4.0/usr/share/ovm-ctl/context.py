from show import getvmby
from webbindings import HTTPException

def addcontext(vmname, key, value, istty, api):
	"""call: 'add context to vm VM with KEY = VALUE'
	description: 'Add a new context item into the key value context storage for the given VM.
	             .Valid keys must not contain whitespace but values may.
	             .If a key already exists, it will be overwritten.'
	args: 'VM: Name of the vm to attach the key value data to.
	      .KEY: The key to map the given value to. May not contain whitespace.
	      .VALUE: The value to attach to the given key.'
	errors: 'If the VM does not exist: Return exit code 3'
	"""
	key = key.upper()

	vm = getvmby(vmname, api, what='hostname')
	if not vm:
		if istty:
			print 'VM %s does not exist' % vmname
		return 3

	api.set_context(vmid=vm['vm_id'], key=key, value=value)


def clearcontext(key, vmname, istty, api):
	"""call: 'clear context key KEY from vm VM'
	description: 'Remove the given key value data from the given VM context store.
	             .THIS FUNCTION IS NOT YET IMPLEMENTED'
	args: 'KEY: Key of the data to remove from the key value store
	      .VM: The name of the VM to clear the key value data from.'
	errors: 'If the given vm does not exist, exit code 3 is returned
	        .If the given key does not exist in the context store, exit code 4 is returned'
	"""
	key = key.upper()

	vm = getvmby(vmname, api, what='hostname')
	if not vm: 
		if istty:
			print "VM %s does not exist" % vmname
		return 3

	try:
		raise Exception("This function has not been implemented yet. Stay tuned.")
		# api.set_context(vmid=vm['vmid'],key=key,value=None)
	except HTTPException, e:
		if e.retcode != 404:
			raise
		if istty:
			print 'VM %s does not have context key %s' % (vmname, key)
		return 4

	if istty:
		print 'Removed key %s from vm %s' % (key, vmname)
