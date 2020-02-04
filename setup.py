#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
from __future__ import unicode_literals
import re
import os
from os.path import join, dirname

# Pip package imports
from setuptools import setup, find_packages

# Internal package imports

# Get the project root directory
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

ROOT = dirname(__file__)

RE_REQUIREMENT = re.compile(r'^\s*-r\s*(?P<filename>.*)$')

def is_pkg(line):
    return line and not line.startswith(('--', 'git', '#'))

def read_requirements(filename):
    with open(os.path.join(ROOT_DIR, filename), encoding='utf-8') as f:
        return [line for line in f.read().splitlines() if is_pkg(line)]


long_description = '\n'.join((
    open('README.rst').read(),
    open('CHANGELOG.rst').read(),
    ''
))


install_requires = read_requirements('requirements.txt')
dev_requires = read_requirements('requirements-dev.txt')

setup(
    name='flask-mm',
    version=__import__('flask_mm').__version__,
    description=__import__('flask_mm').__description__,
    long_description=long_description,
    url='https://github.com/szkkteam/flask_mm',
    author='Istvan Rusics',
    author_email='szkkteam1@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Pillow',
        'Flask'
    ],
    tests_require=dev_requires,
    entry_points={
        'mm.storages': [
            'local = flask_mm.storages.local:LocalStorage',
            #'s3 = flask_fs.backends.s3:S3Backend [s3]',
            #'gridfs = flask_fs.backends.gridfs:GridFsBackend [gridfs]',
            #'swift = flask_fs.backends.swift:SwiftBackend [swift]',
            #'mock = flask_fs.backends.mock:MockBackend',
        ],
        'mm.managers' : [
            'file = flask_mm.managers.file:FileManager',
            'image = flask_mm.managers.image:ImageManager',
        ]
    },
    license='MIT',
    use_2to3=False,
    zip_safe=False,
    keywords='',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: System :: Software Distribution',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
    ],
)