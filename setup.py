#!/usr/bin/env python

from setuptools import setup

setup(name='tap-starshipit',
      version='0.0.1',
      description='Singer.io tap for extracting data from the StarShipIt API',
      author='Zookal',
      url='https://www.zookal.com',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_starshipit'],
      install_requires=[
          'backoff==1.8.0',
          'requests==2.21.0',
          'singer-python==5.8.0'
      ],
      entry_points='''
          [console_scripts]
          tap-starshipit=tap_starshipit:main
      ''',
      packages=['tap_starshipit']
)
