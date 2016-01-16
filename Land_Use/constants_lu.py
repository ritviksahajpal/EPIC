import os, logging, datetime, multiprocessing, pdb, ast, errno
import logging.handlers
from ConfigParser import SafeConfigParser

# Parse config file
parser = SafeConfigParser()
parser.read('../config_EPIC.txt')

###############################################################################
# User modifiable values
#
#
###############################################################################
OUT_TAG        = parser.get('PROJECT','OUT_TAG')
START_YEAR     = parser.getint('PARAMETERS','LU_START_YEAR')
END_YEAR       = parser.getint('PARAMETERS','LU_END_YEAR')
METRIC         = parser.get('PROJECT','LU_METRIC')
TAG            = parser.get('PROJECT','LU_TAG') + '_' + METRIC            #
SET_SNAP       = parser.getboolean('PARAMETERS','SET_SNAP')
REPLACE        = parser.getboolean('PARAMETERS','REPLACE')
USE_INTERIM    = parser.getboolean('PARAMETERS','USE_INTERIM')
DO_MOSAIC      = parser.getboolean('PARAMETERS','DO_MOSAIC')
FILTER_SIZE    = parser.getint('PARAMETERS','FILTER_SIZE')
list_st        = ast.literal_eval(parser.get('PROJECT','LIST_STATES'))
project_name   = parser.get('PROJECT','project_name')

# Maximum number of cpus to use at a time
max_threads = multiprocessing.cpu_count() - 1

# Directories
prj_dir  = parser.get('PATHS','prj_dir')+os.sep                 # Get relative path
cdl_dir  = prj_dir+os.sep+'CropIntensity'+os.sep+'input'+os.sep # Contains input CDL files
base_dir = prj_dir+os.sep+'Lake_States'+os.sep
epic_dir = base_dir+os.sep+'EPIC'+os.sep+project_name+os.sep+'Data'+os.sep+'LU'
inp_dir  = base_dir+'Code'+os.sep+'Python'+os.sep+'open_lands_conversion'+os.sep
out_dir  = base_dir+'output'+os.sep+TAG+os.sep
log_dir  = parser.get('PATHS', 'out_dir') + os.sep + parser.get('PROJECT', 'project_name') + os.sep + \
           parser.get('PROJECT', 'LOGS') + os.sep + OUT_TAG + os.sep

# Directories of GIS input file
pad_dir   = base_dir+'Data'+os.sep+'GIS'+os.sep+'PAD_USA'+os.sep
bound_dir = base_dir+'Data'+os.sep+'GIS'+os.sep+'State_Boundaries'+os.sep
lcc_dir   = base_dir+'Data'+os.sep+'GIS'+os.sep+'Land_Capability_Classes'+os.sep+'GIS_Files'+os.sep

# CONSTANTS
M2_TO_HA   = parser.getfloat('CONSTANTS', 'M2_TO_HA')
CONVERSION = parser.get('CONSTANTS', 'CONVERSION')
RECL       = parser.get('CONSTANTS', 'RECL')
BOUNDARIES = bound_dir + 'states.shp'

OPEN       = parser.getint('CONSTANTS','OPEN')
REMAP_FILE = inp_dir+'recl_EPIC.txt'

def make_dir_if_missing(d):
    try:
        os.makedirs(d)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

# make output dir
make_dir_if_missing(out_dir)
make_dir_if_missing(log_dir)

# logging
LOG_FILENAME   = log_dir + os.sep + 'Log_' + TAG + '_' + OUT_TAG + '.txt'
logging.basicConfig(filename = LOG_FILENAME, level=logging.DEBUG,\
                    format='%(asctime)s    %(levelname)s %(module)s - %(funcName)s: %(message)s',\
                    datefmt="%Y-%m-%d %H:%M:%S") # Logging levels are DEBUG, IN    FO, WARNING, ERROR, and CRITICAL
# Add a rotating handler
logging.getLogger().addHandler(logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10, backupCount=5))
# Output to screen
logging.getLogger().addHandler(logging.StreamHandler())