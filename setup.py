######!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Xavier Robert <xavier.robert@ird.fr>
# SPDX-License-Identifier: GPL-3.0-or-later


from setuptools import setup, find_packages

# Import of the lib pyVertProf
import pyThGIS

def readme():
	with open('README.rst') as f:
		return f.read()

setup(name='pyThGIS',
	#version='0.1.1',
	version=pyThGIS.__version__,
	description='package that provides tools to clean shp Therion output',
	long_descritpion=open('README.rst').read(),
	url='https://github.com/robertxa/pyThGIS',
	download_url='https://github.com/robertxa/pyThGIS/archive/master.zip',
	author='Xavier Robert',
	author_email='xavier.robert@univ-grenoble-alpes.fr',
	license='GPL-V3.0',
	packages=find_packages(),
	install_requires=[
	      'fiona',
		  'shapely',
		  'pandas',
		  'geopandas',
		  'alive_progress'
	],
	classifiers=[
		#"Programming language :: Python",
		"Operating System :: OS Independent",
		#"Programming Language :: Python :: 3",
		"Topic :: Scientific/Engineering :: Visualization"
	#	"Topic :: Scientific/Engineering :: GIS"
	],
	include_package_data=True,
	zip_safe=False)
      