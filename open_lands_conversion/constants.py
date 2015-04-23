import os, multiprocessing, logging, ast
from ConfigParser import SafeConfigParser

# Parse config file
parser = SafeConfigParser()
parser.read('config_open_lands.txt')

###############################################################################
# User modifiable values
#
#
###############################################################################
START_YEAR     = parser.getint('PARAMETERS','START_YEAR') 
END_YEAR       = parser.getint('PARAMETERS','END_YEAR') 
METRIC         = parser.get('PROJECT','METRIC')
TAG            = parser.get('PROJECT','TAG')+METRIC            #
DO_WHEAT       = parser.getboolean('PARAMETERS','DO_WHEAT')
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
prj_dir     = parser.get('PATHS','prj_dir')+os.sep                 # Get relative path
cdl_dir     = prj_dir+os.sep+'CropIntensity'+os.sep+'input'+os.sep # Contains input CDL files
base_dir    = prj_dir+os.sep+'Lake_States'+os.sep
epic_dir    = base_dir+os.sep+'EPIC'+os.sep+project_name+os.sep+'Data'+os.sep+'LU'
inp_dir     = base_dir+'Code'+os.sep+'Python'+os.sep+'open_lands_conversion'+os.sep
out_dir     = base_dir+'output'+os.sep+TAG+os.sep
shared_dir  = base_dir+'shared'+os.sep+TAG+os.sep

# Directories of GIS input file 
pad_dir     = base_dir+'Data'+os.sep+'GIS'+os.sep+'PAD_USA'+os.sep
bound_dir   = base_dir+'Data'+os.sep+'GIS'+os.sep+'State_Boundaries'+os.sep
lcc_dir     = base_dir+'Data'+os.sep+'GIS'+os.sep+'Land_Capability_Classes'+os.sep+'GIS_Files'+os.sep

# CONSTANTS
M2_TO_HA    = parser.getfloat('CONSTANTS','M2_TO_HA')
CONVERSION  = parser.get('CONSTANTS','CONVERSION')
RECL        = parser.get('CONSTANTS','RECL')
BOUNDARIES  = bound_dir+'states.shp'
LCC_CSV     = lcc_dir+'48States.csv'
LCC_CR      = lcc_dir+'lcc_cr'
DI_PI_CSV   = lcc_dir+'US_Comp_20120429.csv'
DI_PI_CR    = lcc_dir+'di_pi_cr'

SSURGO_REMAP_FILE = lcc_dir+'recl.txt'
PI_REMAP_FILE = lcc_dir+'recl_PI.txt'
DI_REMAP_FILE = lcc_dir+'recl_DI.txt'  

WHEAT       = parser.getint('CONSTANTS','WHEAT')
CORN        = parser.getint('CONSTANTS','CORN')
SOY         = parser.getint('CONSTANTS','SOY')
OPEN        = parser.getint('CONSTANTS','OPEN')
FOREST      = parser.getint('CONSTANTS','FOREST')
URBAN       = parser.getint('CONSTANTS','URBAN')
WATER       = parser.getint('CONSTANTS','WATER')
OTHER       = parser.getint('CONSTANTS','OTHER')
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

###############################################################################
#
#
#
#
###############################################################################
def make_dir_if_missing(d):
    if not os.path.exists(d):
        os.makedirs(d)

# make output dir
make_dir_if_missing(out_dir)
make_dir_if_missing(shared_dir)

# logging
LOG_FILENAME   = out_dir+os.sep+'Log_'+TAG+'.txt'
logging.basicConfig(filename = LOG_FILENAME, level=logging.DEBUG,\
                    format='%(asctime)s    %(levelname)s %(module)s - %(funcName)s: %(message)s',\
                    datefmt="%Y-%m-%d %H:%M:%S") # Logging levels are DEBUG, IN    FO, WARNING, ERROR, and CRITICAL