######!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2020 Xavier Robert <xavier.robert@ird.fr>
# SPDX-License-Identifier: GPL-3.0-or-later


"""
#############################################################
#                                                        	#  
#          Script to enhance Therion shapefiles             #
#                                                        	#  
#                 By Xavier Robert                       	#
#            Grenoble, oct. 2022 - jan. 2025               	#
#                                                        	#  
#############################################################

Written by Xavier Robert, oct. 2022 - jan. 2025

xavier.robert@ird.fr

"""

# Do divisions with Reals, not with integers
# Must be at the beginning of the file
from __future__ import division

# Import Python modules
#import numpy as np
import fiona
import shapely
from shapely.geometry import Polygon, LineString
import geopandas as gpd
import pandas as pd
import sys, os, copy, shutil
#from functools import wraps
from alive_progress import alive_bar              # https://github.com/rsalmei/alive-progress	

#################################################################################################
#################################################################################################

def validate(inputfile, rec):
    """_summary_

    Args:
        inputfile (str): Name of the shp input file
        rec (_type_): record from the shp input file

    Raises:
        TopologicalError: _description_

    Returns:
        rec2 (_type_): corrected record to be used to uptade the input file
    """

    rec2 = rec

    if not Polygon(rec['geometry']['coordinates'][0]).is_valid:
        print('Problem in %s geometry' %(inputfile))
        print('%s is not a valid geometric object' %(rec['properties']['_ID']))
        raise TopologicalError('\033[91mERROR:\033[00m Correction does not work...\n%s is not a valid geometric object\n\t The error is: %s' %(str(rec['properties']['_ID']), shapely.validation.explain_validity(rec)))
        #print('We try to correct it')
        #rec2b = shapely.validation.make_valid(Polygon(rec['geometry']['coordinates'][0]))
        # Check à améliorer, il faut que ce soit un Polygon, et non un MultiPolygon...
        #if not rec2b.is_valid:
        #    raise TopologicalError('ERROR: Correction failed...\n%s is not a valid geometric object\n\t The error is: %s' %(str(rec['properties']['_ID']), shapely.validation.explain_validity(rec)))
        #else:
        #    rec2['geometry']['coordinates'][0] = list(rec2b.exterior.coords)

    # Find where there is the error if possible  
    #Diagnostics
    #validation.explain_validity(ob):
    #Returns a string explaining the validity or invalidity of the object.
    #The messages may or may not have a representation of a problem point that can be parsed out.
    #coords = [(0, 0), (0, 2), (1, 1), (2, 2), (2, 0), (1, 1), (0, 0)]
    #p = Polygon(coords)
    #from shapely.validation import explain_validity
    #shapely.validation.explain_validity(p)
    #'Ring Self-intersection[1 1]'
    #shapely.validation.make_valid(ob)
    #Returns a valid representation of the geometry, if it is invalid. If it is valid, the input geometry will be returned.

    # In many cases, in order to create a valid geometry, 
    # the input geometry must be split into multiple parts or multiple geometries. 
    # If the geometry must be split into multiple parts of the same geometry type, 
    # then a multi-part geometry (e.g. a MultiPolygon) will be returned. 
    # If the geometry must be split into multiple parts of different types, 
    # then a GeometryCollection will be returned.
    # For example, this operation on a geometry with a bow-tie structure:
    #from shapely.validation import make_valid
    #coords = [(0, 0), (0, 2), (1, 1), (2, 2), (2, 0), (1, 1), (0, 0)]
    #p = Polygon(coords)
    #make_valid(p)
    #<MULTIPOLYGON (((1 1, 0 0, 0 2, 1 1)), ((2 0, 1 1, 2 2, 2 0)))>
    #Yields a MultiPolygon with two parts, and sometimes area + line:

    return rec2

#################################################################################################
def cutareas(pathshp, outlines, outputspath):
    """
    Function to cut shapefiles areas with the outline to only keep the lines inside the outline

    Args:
        pathshp (str)           : path where are stored output shp from Therion
        outlines (geopandas obj): the outline shapefile
        outputspath (str)       : path where to copy the gpkg files
    """

    print('Working with areas...')
    # 2- Validate the outline and Areas shapefile ; not working yet!
    #for rec in outlines:
    #    rec2 = validate('outline2d.shp', rec)
    #    # update correction --> To do ?
    #    #if rec2 != rec:
    #for rec in areas:
    #    rec2 = validate('areas2d.shp', rec)
    #    # update correction
    #    #if rec2 != rec:

    #   Read the Line Shapefile
    areas = gpd.read_file(pathshp + 'areas2d.shp', driver = 'ESRI shapefile')

    # Extract the intersections between outlines and lines
    # be careful, for this operation, geopandas needs to work with rtree and not pygeos
    #   --> uninstall pygeos and install rtree
    try:
        areasIN = areas.overlay(outlines, how = 'intersection')
    except:
        print('ERROR: 1) uninstall pygeos and install rtree\n\t2) check your polygons validity')
        import rtree
        print ('\tYou may check the validity of your polygons with the verify function in QGIS')
        areasIN = areas.overlay(outlines, how = 'intersection')
        
    # Removes inner lines that have different id and scrap_id
    areasIN = areasIN[areasIN['_SCRAP_ID'] == areasIN ['_ID']]

    # Save output
    #areasIN.to_file("areas2dMasekd.gpkg", driver = "GPKG", encoding = 'utf8')
    areasIN.to_file(outputspath + "areas2dMasekd.gpkg", driver = "GPKG")

    return

#################################################################################################
def cutLines(pathshp, outlines, outputspath):
    """
    Function to cut shapefiles lines with the outline to only keep the lines inside the outline

    Args:
        pathshp (str)           : path where are stored output shp from Therion
        outlines (geopandas obj): the outline shapefile
        outputspath (str)       : path where to copy the gpkg files
    """

    print('Working with lines...')
    #   Read the Line Shapefile
    lines = gpd.read_file(pathshp + 'lines2d.shp', driver = 'ESRI shapefile')
    
    # Vérify if outlines is GeoDataFrame
    if not isinstance(outlines, gpd.GeoDataFrame):
        print("outlines n'est pas un GeoDataFrame. Tentative de conversion...")
        outlines = gpd.read_file(pathshp + 'outline2d.shp')  # Lire un fichier shapefile si outlines est une chaîne de caractères
    
    # Extract lines that are not masked by the outline
    linesOUT = pd.concat((lines[lines['_TYPE'] == 'centerline'],
                           lines[lines['_TYPE'] == 'water_flow'],
                           lines[lines['_TYPE'] == 'label'],
                           lines[lines['_CLIP'] == 'off']),
                           ignore_index=True)

    # Extract lines will be masked by the outline
    linesIN = lines[lines['_CLIP'] != 'off']
    linesIN = linesIN[linesIN['_TYPE'] != 'centerline']
    linesIN = linesIN[linesIN['_TYPE'] != 'water_flow']
    linesIN = linesIN[linesIN['_TYPE'] != 'label']

    # Extract the intersections between outlines and lines
    # be careful, for this operation, geopandas needs to work with rtree and not pygeos
    #   --> uninstall pygeos and install rtree
    try:
        linesIN = linesIN.overlay(outlines, how = 'intersection', keep_geom_type=True)
    except:
        print('\033[91mERROR: 1\033[00m) uninstall pygeos and install rtree\n\t2) check your polygons validity')
        import rtree
        print ('\tYou may check the validity of your polygons with the verify function in QGIS')
        linesIN = linesIN.overlay(outlines, how = 'intersection', keep_geom_type=True)
        print('TEST')

    # Removes inner lines that have different id and scrap_id
    linesIN = linesIN[linesIN['_SCRAP_ID'] == linesIN ['_ID']]

    # Merge the IN and OUT database 
    linesTOT = pd.concat((linesOUT, linesIN),
                           ignore_index=True)

    # Save output
    #linesTOT.to_file("lines2dMasekd.gpkg", driver="GPKG", encoding = 'utf8')
    linesTOT.to_file(outputspath + "lines2dMasekd.gpkg", driver="GPKG")

    return

#################################################################################################
def AddAltPoint(pathshp, outputspath):
    """
    Function to add the altitude of the stations and entrances in the attribut table

    Args:
        pathshp (str)    : path where are stored output shp from Therion
        outputspath (str): path where to copy the gpkg files
    """


    print('Working with points...')
    files = ['points2d', 'stations3d']

    # Open the text file with the coordinates of the caves
    #   This text file (Caves.txt) should be build with Therion compilation
    #   and stored in the output's shapefiles folder
    #      export cave-list -location on -o Outputs/SHP/Caves.txt
    #f = open(pathshp + 'Caves.txt', 'r').readlines() 

    for file in files:
        print('\tupdating %s...' %(file + '.shp'))
        # Make a new shapefile instance
        with fiona.open(pathshp + file + '.shp', 'r') as inputshp:
            # Créer le nouveau schéma des shapefiles
            newschema = inputshp.schema
            newschema['properties']['_ALT'] = 'str:4'
            newschema['properties']['_EASTING'] = 'float'
            newschema['properties']['_NORTHING'] = 'float'
            # Open the output shapefile
            #with fiona.open(inputfile[:-4] + 'Alt.shp', 'w', crs=inputshp.crs, driver='ESRI Shapefile', schema=newschema) as ouput:
            #with fiona.open('points2dAlt.gpkg', 'w', crs=inputshp.crs, driver='GPKG', schema=newschema, encoding = 'utf8') as ouput:
            with fiona.open(outputspath + file + 'Alt.gpkg', 'w', crs=inputshp.crs, driver='GPKG', schema=newschema) as ouput:
                with alive_bar(len(inputshp), title = "\x1b[32;1m- Processing stations...\x1b[0m", length = 20) as bar:
                    # do a loop on the stations
                    for rec in inputshp:
                        # Copy the schema from the input data
                        g = rec
                        # Add Alt, Easting, Northing
                        g['properties']['_ALT'] = str(round(float(rec['geometry']['coordinates'][2])))
                        g['properties']['_EASTING'] = float(rec['geometry']['coordinates'][0])
                        g['properties']['_NORTHING'] = float(rec['geometry']['coordinates'][1])
                        # Write record
                        ouput.write (g)
                        # Update progress bar
                        bar()
    #f.close()
    return


#################################################################################################
def shp2gpkg(pathshp, outputspath):
    """
    function to convert shp files into gpkg files

    Args:
        pathshp (str)    : path where are stored output shp from Therion
        outputspath (str): path where to copy the gpkg files
    """

    # files to be converted
    files = ['outline2d', 'shots3d', 'walls3d']

    print('shp2gpkg : ', files)
    with alive_bar(len(files), title = "\x1b[32;1m- Processing shp2pkg...\x1b[0m", length = 20) as bar:
        for fname in files :
            if fname == 'walls3d':
                print('shp2gpkg does not support walls3d files...\n\t I am only copying the shp file into the right folder')
                for ftype in ['.shp', '.dbf', '.prj', '.shx']:
                    shutil.copy2(pathshp + fname + ftype, outputspath + fname + ftype)
                #pass
                #input = gpd.read_file(fname + '.shp', layer = 'walls3d', driver = 'ESRI shapefile')
                #input.to_file(fname + ".gpkg", driver="GPKG", encoding = 'utf8')
                #with fiona.open(fname + '.shp', 'r') as inputshp:
                #    with fiona.open(fname + '.gpkg', 'w', crs=inputshp.crs, driver='GPKG', schema=inputshp.schema, encoding = 'utf8') as ouput:
                #        for rec in inputshp:
                #            # Write record
                #            ouput.write (g)
            else:
                input = gpd.read_file(pathshp + fname + '.shp', driver = 'ESRI shapefile')
                #input.to_file(fname + ".gpkg", driver="GPKG", encoding = 'utf8')
                input.to_file(outputspath + fname + ".gpkg", driver="GPKG")
            bar()

    return

#################################################################################################
def ThCutAreas(pathshp, outputspath):

    print(' ')
    print('****************************************************************')
    print('Program to cut areas and lines that are intersecting the outline')
    print('        Written by X. Robert, ISTerre')
    print('                October 2022      ')
    print('****************************************************************')
    print(' ')

    # Check if areas, lines and outline shapefiles exists...
    areaOK = True
    for fname in ['outline2d', 'lines2d', 'areas2d', 
                  'shots3d','walls3d']:
        if not os.path.isfile(pathshp + fname + '.shp'):
            if fname == 'areas2d':
                areaOK = False
            else:
                raise NameError('\033[91mERROR:\033[00m File %s does not exist' %(str(pathshp + fname + '.shp')))
    # Check if Outputs path exists
    if not os.path.exists(outputspath):
        print ('\033[91mWARNING:\033[00m ' + outputspath + ' does not exist, I am creating it...')
        os.mkdir(outputspath)

    #1- Read the outline shapefile
    outlines = gpd.read_file(pathshp + 'outline2d.shp', driver = 'ESRI shapefile')
    
    print('Check')
    ## Change SHP to gpkg
    #shp2gpkg(pathshp, outputspath)
    ## Work with points
    #AddAltPoint(pathshp, outputspath)
    ## Work with lines
    cutLines(pathshp, outlines, outputspath)
    ## Work with Areas
    if areaOK:
        print ('Cuting areas...')
        cutareas(pathshp, outlines, outputspath)
    else:
        print ("No areas to process...")
    
    #5- End ?

    print('')
    print('Update point, areas and lines done.')
    print('')

def runThGIS(pathshp, outputspath):
    
    # Add the altitude to the shapefiles :
    AddAltPoint(pathshp, outputspath)

    # Run the transformation
    ThCutAreas(pathshp, outputspath)

    # Write gpkg
    shp2gpkg(pathshp, outputspath)


    return


######################################################################################################
if __name__ == u'__main__':	
	###################################################
    # initiate variables
    #inputfile = 'stations3d.shp'
    pathshp = '../Test/SHP/'
    outputspath = '../Test/GPKG/'
    ###################################################
    runThGIS(pathshp, outputspath)

    # Run the transformation
    #ThCutAreas(pathshp, outputspath)

    # End...

