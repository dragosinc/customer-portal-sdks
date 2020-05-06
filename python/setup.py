#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('LICENSE') as license_file:
    license = license_file.read()

requirements = [
    "requests"
]

test_requirements = [
]

setup(
    name='dragos-portal-python',
    version='0.1.0',
    description="A simple Python wrapper client for the Dragos portal API",
    long_description=readme,
    author="Dragos, Inc.",
    author_email="",
    url='https://github.com/dragosinc/dragos-portal-python',
    packages=find_packages(exclude=('tests', 'docs')),
    include_package_data=True,
    install_requires=requirements,
    license=license,
    zip_safe=True,
    keywords='dragos',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
