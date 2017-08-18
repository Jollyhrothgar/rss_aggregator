#!/usr/bin/env python
"""
ML_RSS setup file.
"""
from setuptools import setup


# Dynamically retrieve the version information from the MLPUXBOT module
ML_RSS = __import__('ml_rss')
VERSION = ML_RSS.__version__
AUTHOR = ML_RSS.__author__
AUTHOR_EMAIL = ML_RSS.__email__
DESCRIPTION = ML_RSS.__doc__

with open('requirements.txt') as requirements:
    REQUIREMENTS = requirements.readlines()

setup(
    name='ml_rss',
    version=VERSION,
    setup_requires=['setuptools-markdown'],
    long_description_markdown_filename='readme.md',
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages=[
        'ml_rss',
    ],
    package_dir={'ml_rss': 'ml_rss'},
    include_package_data=True,
    install_requires=REQUIREMENTS,
    license='BSD',
    zip_safe=True,
    platforms=['any'],
    keywords=['rss', 'nlp'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',
        'Topic :: Internet',
        'Programming Language :: Python :: 3.5',
    ],
)
