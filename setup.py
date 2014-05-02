#!/usr/bin/env python

from setuptools import setup
import os

from ovm_ctl import __version__

data_files = [
        ('ovm_ctl', ['ovm_ctl/ca.pem', 'ovm_ctl/extra'])
]
man_dir = "/usr/local/man"
if os.path.isdir(man_dir):
	data_files.append( (man_dir + '/man1', ['manpage/ovm-ctl.1']) ) 

setup(name='ovm_ctl',
    version=__version__,
    license='BSD Simplified 2-clause licence',
    description='Python bindings and command line utility for the OrionVM IaaS platform',
    long_description=open('README').read(),
    url='https://github.com/orionvm/ovm-ctl',
    maintainer='Chris McClymont',
    maintainer_email='chris.mcclymont@orionvm.com',
    packages=['ovm_ctl'],
    scripts=['ovm_ctl/ovm-ctl'],
    package_data={
        'ovm_ctl': [ 'version', ],
    },
    data_files=data_files,
    zip_safe=False
)
