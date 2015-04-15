import os, sys, logging, pdb, getopt, glob, zipfile, arcpy, csv, time, datetime, errno, us, fnmatch, argparse
import pandas as pd
import numpy as np
from scipy.stats import mode
from arcpy.sa import *
from dbfpy import dbf

# ArcGIS constants
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput = True
arcpy.env.extent = "MAXOF"

##################################################################
# Input directory structure
# base_dir contains all the inputs and the output directory
# SOIL: contains SSURGO soil data
# BOUNDARY: contains county boundary data
# WSHD: contains 10 digit watershed boundary data
# LANDUSE: contains CDL based crop rotations
# OUTPUT: contains output
# OUTPUT\combined: subfolder within output contains the combined raster
##################################################################
LIST_STATES = 'StateNames_LakeStates.csv'
base_dir    = os.sep.join(os.path.dirname(__file__).split(os.sep)[:-3])#r'C:\Users\ritvik\Documents\PhD\Projects\SEIMF'
SOIL = 'ssurgo'
BOUNDARY = 'county'
WSHD = '10digit'
LANDUSE = 'cdl'
DEM = 'dem'
OUTPUT = 'output'
SHPFILES = 'shapefiles'
COMBINED = 'combined'
COM = 'com'
CATALOG= 'catalog'

in_ssurgo_dir = base_dir+os.sep+SOIL
in_county_dir = base_dir+os.sep+BOUNDARY
in_ndhd_dir   = base_dir+os.sep+WSHD+os.sep+SHPFILES
in_dem_dir    = base_dir+os.sep+DEM
in_cdl_dir    = base_dir+os.sep+LANDUSE
out_dir       = base_dir+os.sep+OUTPUT
states_file   = base_dir+os.sep+'StateNames_1.csv'

logging.basicConfig(filename = out_dir+os.sep+'log.txt', level = logging.DEBUG, filemode = 'a')
# All other features are reprojected to the projection and resolution of the CDL layer
CDL_RESOLUTION = 56
any_errors = False


dates      = datetime.datetime.now().strftime("mon_%m_day_%d_%H_%M")
base_dir   = os.sep.join(os.path.dirname(__file__).split(os.sep)[:-3])
cdl_dir    = base_dir+os.sep+'Data'+os.sep+'GIS'+os.sep+'CDL'+os.sep
data_dir   = base_dir+os.sep+'Data'+os.sep+'GIS'+os.sep+'SSURGO'+os.sep
sto_dir    = base_dir+os.sep+'Data'+os.sep+'GIS'+os.sep+'STATSGO'+os.sep
out_dir    = base_dir+os.sep+'output'+os.sep+TAG+os.sep+'SSURGO_to_csv'+os.sep+TAG+'_'+dates+os.sep
epic_dir   = base_dir+os.sep+'output'+os.sep+TAG+os.sep+'SSURGO_to_EPIC'+os.sep+TAG+'_'+dates+os.sep

###############################################################################
#
#
#
###############################################################################
def make_dir_if_missing(d):
    try:
        os.makedirs(d)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

# Create directories
make_dir_if_missing(data_dir)
make_dir_if_missing(out_dir)
make_dir_if_missing(epic_dir)

# Logging
LOG_FILENAME   = out_dir+os.sep+'Log_'+TAG+'_'+dates+'.txt'
logging.basicConfig(filename = LOG_FILENAME, level=logging.INFO,\
                    format='%(asctime)s    %(levelname)s %(module)s - %(funcName)s: %(message)s',\
                    datefmt="%Y-%m-%d %H:%M:%S") # Logging levels are DEBUG, INFO, WARNING, ERROR, and CRITICAL
logger = logging   