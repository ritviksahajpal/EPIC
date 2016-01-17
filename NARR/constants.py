import os, logging, datetime, util, multiprocessing, pdb, ast
from ConfigParser import SafeConfigParser
import logging.handlers

# Parse config file
parser = SafeConfigParser()
parser.read('../config_EPIC.txt')

###############################################################################
# User modifiable values
#
#
###############################################################################
OUT_TAG     = parser.get('PROJECT','OUT_TAG')
START_YR    = parser.getint('PARAMETERS','START_YR')                  # Starting year of weather data
END_YR      = parser.getint('PARAMETERS','END_YR')                    # Ending year of weather data
LAT_BOUNDS  = ast.literal_eval(parser.get('PARAMETERS','LAT_BOUNDS')) # Lat boundary of study region  
LON_BOUNDS  = ast.literal_eval(parser.get('PARAMETERS','LON_BOUNDS')) # Lon boundary of study region
TAG         = parser.get('PROJECT','NARR_TAG')                        # Tag of NARR folder
EPIC_DLY    = parser.get('PARAMETERS','EPIC_DLY')                     # Name of EPIC daily weather station list file
EPIC_MON    = parser.get('PARAMETERS','EPIC_MON')                     # Name of EPIC monthly weather station list file
WXPMRUN     = parser.get('PARAMETERS','WXPMRUN')
WXPM_EXE    = parser.get('PARAMETERS','WXPM_EXE')
DO_PARALLEL = parser.getboolean('PARAMETERS','NARR_PARLEL')           # Use multiprocessing or not?
DO_SITE     = parser.getboolean('PARAMETERS','DO_SITE')               # Run for single site (True) or not (False)
SITE_LAT    = parser.getfloat('PARAMETERS','SITE_LAT')                # If DO_SITE is True, then lat
SITE_LON    = parser.getfloat('PARAMETERS','SITE_LON')                # If DO_SITE is True, then lon

###############################################################################
# Constants
#
#
###############################################################################
BASE_CMD    = "ftp://ftp.cdc.noaa.gov/Datasets/NARR/Dailies/monolevel/" # Obtain daily mean data
TEMP_CMD    = "ftp://ftp.cdc.noaa.gov/Datasets/NARR/monolevel/"         # For temperature we extract 3 hourly data to get daily min and max
WMsq_MjMsq  = 0.0864                                                    # Convert W m^-2 into Mj m^-2 http://www.fao.org/docrep/x0490e/x0490e0i.htm
K_To_C      = -273.15

# Variables
vars_to_get = {'air.2m':'air','apcp':'apcp','rhum.2m':'rhum','uwnd.10m':'uwnd','vwnd.10m':'vwnd','dswrf':'dswrf','uswrf.sfc':'uswrf'}
# Maximum number of cpus to use at a time
max_threads = multiprocessing.cpu_count() - 1

# Date for file names
strt_date   = datetime.date(START_YR,1,1)
end_date    = datetime.date(END_YR,12,31)

# Directories
meta_dir    = parser.get('PATHS', 'meta_dir') + os.sep
narr_dir    = parser.get('PATHS', 'narr_dir') + os.sep
data_dir    = parser.get('PATHS', 'out_dir') + os.sep + parser.get('PROJECT', 'project_name') + os.sep
log_dir     = parser.get('PATHS', 'out_dir') + os.sep + parser.get('PROJECT', 'project_name') + os.sep + \
              parser.get('PROJECT', 'LOGS') + os.sep + OUT_TAG + os.sep
out_dir     = parser.get('PATHS', 'out_dir') + os.sep + parser.get('PROJECT', 'project_name') + os.sep + \
              parser.get('PROJECT', 'EPIC_dat') + os.sep + OUT_TAG
epic_dly    = parser.get('PATHS', 'out_dir') + os.sep + parser.get('PROJECT', 'project_name') + os.sep + 'inputs' + os.sep \
              + parser.get('PROJECT', 'OUT_TAG') + os.sep + 'daily' + os.sep
epic_mon    = parser.get('PATHS', 'out_dir') + os.sep + parser.get('PROJECT', 'project_name') + os.sep + 'inputs' + os.sep + \
              parser.get('PROJECT', 'OUT_TAG') + os.sep + 'monthly' + os.sep

# Create directories
util.make_dir_if_missing(meta_dir)
util.make_dir_if_missing(narr_dir)
util.make_dir_if_missing(out_dir)
util.make_dir_if_missing(epic_dly)
util.make_dir_if_missing(epic_mon)
util.make_dir_if_missing(log_dir)

# Logging
LOG_FILENAME   = log_dir + os.sep + 'Log_' + TAG + '_' + OUT_TAG + '.txt'
logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO,\
                    format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s',\
                    datefmt="%m-%d %H:%M") # Logging levels are DEBUG, INFO, WARNING, ERROR, and CRITICAL
# Add a rotating handler
logging.getLogger().addHandler(logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=50000, backupCount=5))
# Output to screen
logging.getLogger().addHandler(logging.StreamHandler())

# Check if we want to do just a single site
if DO_SITE:
    LAT_BOUNDS[0] = LAT_BOUNDS[1] = SITE_LAT
    LON_BOUNDS[0] = LON_BOUNDS[1] = SITE_LON



      
