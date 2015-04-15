import os, time, pdb, operator, csv, glob, logging, shutil, arcpy, datetime, numpy, sys, pandas
from dbfpy import dbf
from arcpy.sa import *
from itertools import groupby, combinations, combinations_with_replacement
from collections import Counter

# Arcpy constants
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput= True
arcpy.env.extent         = "MAXOF"

# USER MODIFIED PARAMETERS #####################################################
START_YEAR  = 2008
END_YEAR    = 2013
METRIC      = 'LCC' # 'LCC','DI','PI'
TAG         = 'Apr10_LakeStates_NoWheat7_'+METRIC
list_states = 'MI_MN_WI.txt'#'states_48.txt'
DO_WHEAT    = False
SET_SNAP    = True
REPLACE     = True
USE_INTERIM = False
DO_MOSAIC   = True
FILTER_SIZE = 1
################################################################################

date        = datetime.datetime.now().strftime("mon_%m_day_%d_%H_%M")#'mon_09_day_09_21_52'#

# Directories
prj_dir     = os.sep.join(os.path.dirname(__file__).split(os.sep)[:-4]) # Get relative path
cdl_dir     = prj_dir+os.sep+'CropIntensity\\input\\'                   # Contains input CDL files
base_dir    = prj_dir+os.sep+'Lake_States\\'
inp_dir     = base_dir+'Code\\Python\\open_lands_conversion\\'
out_dir     = base_dir+'output'+os.sep+TAG+'_'+date+os.sep
shared_dir  = base_dir+'shared'+os.sep+TAG+os.sep

# Directories of GIS input file 
pad_dir     = base_dir+'Data\\GIS\\PAD_USA\\'
bound_dir   = base_dir+'Data\\GIS\\State_Boundaries\\'
lcc_dir     = base_dir+'Data\\GIS\\Land_Capability_Classes\\GIS_Files\\'

# CONSTANTS
M2_TO_HA    = 0.0001
CONVERSION  = 'conversion'
RECL        = 'recl'
BOUNDARIES  = bound_dir+'states.shp'
LCC_CSV     = lcc_dir+'48States.csv'
LCC_CR      = lcc_dir+'lcc_cr'
DI_PI_CSV   = lcc_dir+'US_Comp_20120429.csv'
DI_PI_CR    = lcc_dir+'di_pi_cr'

SSURGO_REMAP_FILE = lcc_dir+'recl.txt'
PI_REMAP_FILE = lcc_dir+'recl_PI.txt'
DI_REMAP_FILE = lcc_dir+'recl_DI.txt'  

WHEAT       = 498
CORN        = 499
SOY         = 501
OPEN        = 500
FOREST      = 503
URBAN       = 505
WATER       = 504
OTHER       = 502
CORN_SOY    = [CORN,SOY]
CULTIVATED  = [WHEAT,CORN,SOY,OTHER] # Corn: 499; Soybean: 501; Other crops: 502
REGION      = ['LP','UP']

# Wheat
if(DO_WHEAT):
    FIELDS      = [WHEAT,CORN,SOY,OPEN,FOREST,URBAN,WATER,OTHER]
    LANDUSE     = {'WHEAT':498,'CORN':499,'SOY':501,'OPEN':500,'FOREST':503,'URBAN':505,'WATER':504,'OTHER':502,'CULT':[498,499,501,502]}
    OPP_LU      = {498:'WHEAT',499:'CORN',501:'SOY',500:'OPEN',503:'FOREST',505:'URBAN',504:'WATER',502:'OTHER'}
    CULT        = ['WHEAT','CORN','SOY','OTHER']
    # FILE NAMES
    REMAP_FILE  = inp_dir+'recl.txt'    
else:    
    # No Wheat
    FIELDS      = [CORN,SOY,OPEN,FOREST,URBAN,WATER,OTHER]
    LANDUSE     = {'CORN':499,'SOY':501,'OPEN':500,'FOREST':503,'URBAN':505,'WATER':504,'OTHER':502,'CULT':[499,501,502]}
    OPP_LU      = {499:'CORN',501:'SOY',500:'OPEN',503:'FOREST',505:'URBAN',504:'WATER',502:'OTHER'}
    CULT        = ['CORN','SOY','OTHER']
    # FILE NAMES
    REMAP_FILE  = inp_dir+'recl_NoWheat7.txt'#'recl_Johnston.txt'#'recl_NoWheat.txt'
