#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.readlines()

with open('test_requirements.txt') as test_requirements_file:
    test_requirements = test_requirements_file.readlines()

setup(
    name='overscaler',
    version='0.1.0',
    description="Service for autoscaling Stateful Sets in Google Kubernetes Engine",
    long_description=readme + '\n\n' + history,
    author="Gleam AI",
    url='https://github.com/GleamAI/overscaler',
    packages=[
        'overscaler'
    ],
    package_dir={'overscaler':
                 'overscaler'},
    entry_points={
        'console_scripts': [
            'overscaler=overscaler.overcli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='overscaler',
    classifiers=[
        'Development Status :: 1 - Pre-Alpha',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5'
    ],
    test_suite='tests',
    tests_require=test_requirements
)
