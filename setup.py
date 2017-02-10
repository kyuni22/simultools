# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='simultools',
      version='0.0.2',
      description='tools for backtesting and other trading issues',
      url='https://github.com/kyuni22/simultools',
      author='kyuni22',
      author_email='kyuni22@gmail.com',
      license='MIT',
      packages=['simultools'],
      install_requires=[
          'pandas', 'numpy'
      ],
      zip_safe=False)