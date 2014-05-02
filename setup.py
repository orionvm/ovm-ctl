#!/usr/bin/env python

from setuptools import setup
from ovm_ctl import __version__

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
        'ovm_ctl': [ 'ca.pem', 'extra' ],
    },
    data_files=[ ('man/man1', ['manpage/ovm-ctl.1']) ],
    zip_safe=False
)
