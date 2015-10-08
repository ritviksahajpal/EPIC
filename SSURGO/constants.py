import os, sys, logging, pdb, errno, multiprocessing, ast
from ConfigParser import SafeConfigParser

# Parse config file
parser = SafeConfigParser()
parser.read('../config_EPIC.txt')

###############################################################################
# User modifiable values
#
#
###############################################################################
TAG            = parser.get('PROJECT','TAG')          # Tag of SSURGO folder
ZERO_LINES     = parser.getint('PARAMETERS','ZERO_LINES')
SLLIST         = parser.get('PARAMETERS','SLLIST')
cdl_res        = parser.getint('PARAMETERS','SIZE')  
list_st        = ast.literal_eval(parser.get('PROJECT','LIST_STATES'))
all            = parser.get('PARAMETERS','all') 
dominant       = parser.get('PARAMETERS','dominant') 

###############################################################################
# Constants
#
#
###############################################################################
SSURGO_SEP     = '|'
MUAGGATT       = 'muaggatt'
COMPONENT      = 'comp'
MAPUNIT        = 'mapunit'
CHORIZON       = 'chorizon'
CHFRAGS        = 'chfrags'
SPATIAL        = 'spatial'
TABULAR        = 'tabular'
MUKEY          = 'MUKEY'
CONV_DEPTH     = 0.01    # cm to m
CONV_KSAT      = 3.6     # mm/sec to mm/h
OM_TO_WOC      = 0.58    # organic matter to C
SOIL           = 'ssurgo'
OUTPUT         = 'output'
LANDUSE        = 'cdl'
INPUT          = 'input'


epic_soil_vars = {33:'sandtotal_r',51:'silttotal_r',60:'claytotal_r',66:'om_r',\
                  72:'dbthirdbar_r',78:'dbovendry_r',82:'ksat_r',85:'awc_r',\
                  91:'wthirdbar_r',94:'wfifteenbar_r',114:'caco3_r',\
                  126:'cec7_r',132:'sumbases_r',135:'ph1to1h2o_r'}
hydgrp_vars    = {'hydgrp':{'A':1,'B':2,'C':3,'D':4,'A/D':1,'B/D':2,'C/D':3}}

mapunit_vars   = {1:'muname',4:'muacres',23:'mukey'} #0:'musym'
component_vars = {1:'comppct_r',9:'slope_r',12:'slopelenusle_r',25:'elev_r',\
                  28:'aspectrep',32:'albedodry_r',79:'hydgrp',107:'mukey',108:'cokey'}
chorizon_vars  = {6:'hzdept_r',9:'hzdepb_r',33:'sandtotal_r',51:'silttotal_r',\
                  60:'claytotal_r',66:'om_r',72:'dbthirdbar_r',78:'dbovendry_r',\
                  82:'ksat_r',85:'awc_r',91:'wthirdbar_r',94:'wfifteenbar_r',\
                  114:'caco3_r',126:'cec7_r',132:'sumbases_r',135:'ph1to1h2o_r',\
                  169:'cokey',170:'chkey'}
muaggatt_vars  = {3:'slopegraddcp',4:'slopegradwta',5:'brockdepmin',6:'wtdepannmin',\
                  11:'aws025wta',12:'aws050wta',13:'aws0100wta',14:'aws0150wta',\
                  20:'niccdcd',21:'niccdcdpct',39:'mukey'}
chfrags_vars   = {1:'Fragvol_r',10:'chkey'}

base_dir   = parser.get('PATHS','base_dir')+os.sep
data_dir   = parser.get('PATHS','srgo_dir')+os.sep
out_dir    = parser.get('PATHS','out_dir')+os.sep+parser.get('PROJECT','project_name')+os.sep+parser.get('PATHS', 'sims_dir')
r_soil_dir = parser.get('PATHS','out_dir')+os.sep+parser.get('PROJECT','project_name')+os.sep+'Data'+os.sep
t_soil_dir = parser.get('PATHS','out_dir')+os.sep+parser.get('PROJECT','project_name')+os.sep+'inputs/soils'+os.sep

# Maximum number of cpus to use at a time
max_threads = multiprocessing.cpu_count() - 1

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
make_dir_if_missing(r_soil_dir)
make_dir_if_missing(t_soil_dir)

# Logging
LOG_FILENAME   = os.path.dirname(out_dir)+os.sep+'Log_'+TAG+'.txt'
logging.basicConfig(filename = LOG_FILENAME, level=logging.INFO,\
                    format='%(asctime)s    %(levelname)s %(module)s - %(funcName)s: %(message)s',\
                    datefmt="%Y-%m-%d %H:%M:%S") # Logging levels are DEBUG, INFO, WARNING, ERROR, and CRITICAL