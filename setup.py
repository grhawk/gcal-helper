#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
doclink = """
Documentation
-------------

The full documentation is at http://gcal_ideal_week_helper.rtfd.org."""
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='gcal_ideal_week_helper',
    version='0.1.0',
    description='Let's start something wonderfull!',
    long_description=readme + '\n\n' + doclink + '\n\n' + history,
    author='Riccardo Petraglia',
    author_email='riccardo.petraglia@gmail.com',
    url='https://github.com/grhawk/gcal_ideal_week_helper',
    packages=[
        'gcal_ideal_week_helper',
    ],
    package_dir={'gcal_ideal_week_helper': 'gcal_ideal_week_helper'},
    include_package_data=True,
    install_requires=[
    ],
    license='MIT',
    zip_safe=False,
    keywords='gcal_ideal_week_helper',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
