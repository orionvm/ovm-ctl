import show
import create
import attach
import detach
import boot
import shutdown
import console
import destroy

# This file contains the regex patterns that define our commands.
# It's a weird way to do things but it's worked out quite nice.

# route: (fixed string for pre-matching, regex, function)

showroutes = [('show ips', r'^show ips$', show.showips),\
              ('show ip', r'show ip ([^ ]+)$', show.showip),\
              ('show vms', r'^show vms$', show.showvms),\
              ('show vm', r'^show vm ([^ ]+)$', show.showvm),\
              ('show disks', r'^show disks$', show.showdisks),\
              ('show disk', r'^show disk ([^ ]+)$', show.showdisk),\
              ('show usage', r'^show usage$', show.showuse),\
              ('show balance', r'^show (?:balance|me the money)$', show.showbalance),\
              ('show images', r'^show images$', show.showimages)]

createroutes = [('create disk', r'^create disk ([^ ]+) with size ([^ ]+)(?: and image ([^ ]+))?$', create.createdisk), \
                ('create ip', r'^create ip with friendly ([^ ]+)$', create.createip),\
                ('create vm', r'^create vm ([^ ]+) with ram ([0-9]+[MG])$', create.createvm),\
                ('clone disk', r'^clone disk ([^ ]+) from ([^ ]+)(?: with size ([^ ]+))?$', create.clonedisk)]


attachroutes = [('attach disk', r'^attach disk ([^ ]+) to ([^ ]+) with target (xv[^ ]+)$', attach.attachdisk),\
                ('attach ip', r'^attach ip ([^ ]+) to vm ([^ ]+)$', attach.attachip)]

detachroutes = [('detach disk', r'^detach disk ([^ ]+) from ([^ ]+)$', detach.detachdisk),\
                ('detach ip', r'^detach ip ([^ ]+) from ([^ ]+)$', detach.detachip)]

bootroutes = [('boot vm', r'^boot vm ([^ ]+)$', boot.bootvm)]

shutdownroutes = [('shutdown vm', r'^shutdown vm ([^ ]+)$', shutdown.shutdownvm)]

consoleroutes = [('console', r'^console ([^ ]+)$', console.runconsole)]

destroyroutes = [('destroy ip', r'^destroy ip ([^ ]+)$', destroy.destroyip),\
                ('destroy disk', r'destroy disk ([^ ]+)$', destroy.destroydisk),\
                ('destroy vm', r'destroy vm ([^ ]+)$', destroy.destroyvm)]

def comment(api,istty):
	"""call: '# COMMENT'
	description: 'A line beginning with a "#" is a comment line. This line will be ignored.
	             .This can be useful when writing scripts to be used with the -f option.'
	"""
	return 0

def quit(*args):
    """call: 'quit'
    description: 'Exit the program. Has no effect if given in command line options.
                 .Note that an EOF (Ctrl-D) can also be used to exit.'
    """
    sys.exit(0)

miscroutes = [('#', r'^(?:#.*)?$', comment),\
              ('quit', r'quit', quit)]

routes = showroutes + createroutes + attachroutes + detachroutes + bootroutes + shutdownroutes + consoleroutes + destroyroutes + miscroutes
