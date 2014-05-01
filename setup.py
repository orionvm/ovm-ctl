#!/usr/bin/env python

from setuptools import setup

from ovm_ctl import __version__

setup(name='ovm_ctl',
    version=__version__,
    long_description=open('README').read(),
    url='https://github.com/orionvm/ovm-ctl',
    packages=['ovm_ctl'],
    scripts=['ovm_ctl/ovm-ctl'],
    package_data={
        'ovm_ctl': [ 'version', ],
    },
    install_requires=[
    ],
    data_files=[
        ('ovm_ctl', ['ovm_ctl/ca.pem', 'ovm_ctl/extra'])
    ]
)
