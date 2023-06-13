#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name='squ',
    version='0.0.1',
    author='Ler2sq',
    author_email='ler2sq@gmail.com',
    url='https://github.com/Squirre17/python-utils',
    description=u'self-used utils',
    packages=['squ'],
    install_requires=[
        "typing",
        "functools",
        "loguru"
    ],
    entry_points={}
)