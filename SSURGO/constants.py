import os, sys, logging, pdb, arcpy, errno, argparse, multiprocessing

# ArcGIS initialization
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput = True
arcpy.env.extent = "MAXOF"

###############################################################################
# User modifiable values
#
#
###############################################################################
TAG            = 'SSURGO'
LIST_STATES    = 'StateNames_LakeStates.csv'
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
CONV_OM_TO_WOC = 0.58    # fraction
ZERO_LINES     = 23      #
SOIL           = 'ssurgo'
OUTPUT         = 'output'
CATALOG        = 'catalog'
LANDUSE        = 'cdl'
CDL_STATE      = 'DE'
INPUT          = 'input'
SLLIST         = 'ieSlList.dat'

epic_soil_vars = {33:'sandtotal_r',51:'silttotal_r',60:'claytotal_r',66:'om_r',\
                  72:'dbthirdbar_r',78:'dbovendry_r',82:'ksat_r',85:'awc_r',\
                  91:'wthirdbar_r',94:'wfifteenbar_r',114:'caco3_r',\
                  126:'cec7_r',132:'sumbases_r',135:'ph1to1h2o_r'}
hydgrp_vars    = {'hydgrp':{'A':1,'B':2,'C':3,'D':4,'A/D':1,'B/D':2,'C/D':3}}

mapunit_vars   = {1:'muname',4:'muacres',23:'mukey'} #0:'musym'
component_vars = {1:'comppct_r',9:'slope_r',32:'albedodry_r',79:'hydgrp',107:'mukey',108:'cokey'}
chorizon_vars  = {6:'hzdept_r',9:'hzdepb_r',33:'sandtotal_r',51:'silttotal_r',\
                  60:'claytotal_r',66:'om_r',72:'dbthirdbar_r',78:'dbovendry_r',\
                  82:'ksat_r',85:'awc_r',91:'wthirdbar_r',94:'wfifteenbar_r',\
                  114:'caco3_r',126:'cec7_r',132:'sumbases_r',135:'ph1to1h2o_r',\
                  169:'cokey',170:'chkey'}
muaggatt_vars  = {3:'slopegraddcp',4:'slopegradwta',5:'brockdepmin',6:'wtdepannmin',\
                  11:'aws025wta',12:'aws050wta',13:'aws0100wta',14:'aws0150wta',\
                  20:'niccdcd',21:'niccdcdpct',39:'mukey'}
chfrags_vars   = {1:'Fragvol_r',10:'chkey'}

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-t','--tag',help='Project name',default='OpenLands_LS')
parser.add_argument('-s','--size',help='Raster resolution',default=56)
args   = vars(parser.parse_args())

cdl_res    = args['size']
#dates     = datetime.datetime.now().strftime("mon_%m_day_%d_%H_%M")
base_dir   = os.sep.join(os.path.dirname(__file__).split(os.sep)[:-3])
cdl_dir    = base_dir+os.sep+'Data'+os.sep+'GIS'+os.sep+'CDL'+os.sep
data_dir   = base_dir+os.sep+'Data'+os.sep+'GIS'+os.sep+'SSURGO'+os.sep
out_dir    = base_dir+os.sep+'EPIC'+os.sep+args['tag']+os.sep
r_soil_dir = out_dir+os.sep+'Data'+os.sep
t_soil_dir = out_dir+os.sep+'soils'+os.sep

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
LOG_FILENAME   = out_dir+os.sep+'Log_'+TAG+'.txt'
logging.basicConfig(filename = LOG_FILENAME, level=logging.INFO,\
                    format='%(asctime)s    %(levelname)s %(module)s - %(funcName)s: %(message)s',\
                    datefmt="%Y-%m-%d %H:%M:%S") # Logging levels are DEBUG, INFO, WARNING, ERROR, and CRITICAL