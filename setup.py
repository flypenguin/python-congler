#!/usr/bin/env python

from setuptools import setup, find_packages
from pip.req import parse_requirements
from pip.download import PipSession

import io


VERSION = "0.5.0"

# auto-generate requirements from requirements.txt
install_reqs = parse_requirements("./requirements.txt", session=PipSession())
reqs = [str(ir.req) for ir in install_reqs]

long_description = (
    io.open('README.rst', encoding='utf-8').read() +
    '\n' +
    io.open('CHANGES.rst', encoding='utf-8').read()
)

setup(
    name         = 'congler',
    py_modules   = ['congler.py'],
    version      = VERSION,
    description  = 'Search and delete consul services',
    author       = 'Axel Bock',
    author_email = 'mr.axel.bock@gmail.com',
    url          = 'https://github.com/flypenguin/python-congler',
    download_url = 'https://github.com/flypenguin/python-congler/tarball/{}'.format(VERSION),
    keywords     = ['consul', 'cli'],
    install_requires = reqs,
    long_description = long_description,
    entry_points     = {
        'console_scripts': [
            'congler=congler:console_entrypoint',
        ],
    },
    classifiers  = [
        "License :: OSI Approved :: MIT License",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Topic :: System :: Systems Administration",
    ],
)
