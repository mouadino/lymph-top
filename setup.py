# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

import sys


with open('README.rst') as f:
    description = f.read()


setup(
    name='lymph-top',
    url='http://github.com/mouadino/lymph-top/',
    version='0.1.0',
    packages=find_packages(),
    license=u'Apache License (2.0)',
    author=u'Mouad Benchchaoui, Jacques Rott',
    maintainer=u'Mouad Benchchaoui',
    maintainer_email=u'mouadino@gmail.com',
    keywords='lymph top monitoring metrics',
    long_description=description,
    include_package_data=True,
    install_requires=[
        'lymph',
        'blessed',
        'hurry.filesize',
    ],
    entry_points={
        'lymph.cli': [
            'top = lymph_top.cli:TopCommand'
        ],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Framework :: Lymph',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3'
    ]
)
