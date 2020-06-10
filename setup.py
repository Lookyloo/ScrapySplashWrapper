#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup  # type: ignore


setup(
    name='ScrapySplashWrapper',
    version='1.0-dev',
    author='Raphaël Vinot',
    author_email='raphael.vinot@circl.lu',
    maintainer='Raphaël Vinot',
    url='https://github.com/Lookyloo/scrapysplashwrapper',
    description='Scrapy splash wrapper as a standalone library.',
    packages=['scrapysplashwrapper'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Telecommunications Industry',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python :: 3',
        'Topic :: Security',
        'Topic :: Internet',
    ],
    install_requires=['scrapy', 'scrapy-splash']
)
