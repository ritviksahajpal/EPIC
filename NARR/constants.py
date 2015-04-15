import os, logging, datetime, util, multiprocessing, argparse
from datetime import date

###############################################################################
# User modifiable values
#
#
###############################################################################
START_YR    = 1979                                                      # Starting year of weather data
END_YR      = 2014                                                      # Ending year of weather data
LAT_BOUNDS  = [41.5,49.5]                                               # Lat boundary of study region  
LON_BOUNDS  = [-98.0,-81.0]                                             # Lon boundary of study region
TAG         = 'NARR'                                                    # Tag of NARR folder
EPIC_DLY    = 'iewedlst.dat'                                            # Name of EPIC daily weather station list file
EPIC_MON    = 'iewealst.dat'                                            # Name of EPIC monthly weather station list file
WXPMRUN     = 'WXPMRUN.DAT'
WXPM_EXE    = 'WXPM3020.exe'
DO_PARALLEL = True                                                      # Use multiprocessing or not?
DO_SITE     = False                                                     # Run for single site (True) or not (False)
SITE_LAT    = 42.0                                                      # If DO_SITE is True, then lat
SITE_LON    = -86.0                                                     # If DO_SITE is True, then lon
BASE_CMD    = "ftp://ftp.cdc.noaa.gov/Datasets/NARR/Dailies/monolevel/" # Obtain daily mean data
TEMP_CMD    = "ftp://ftp.cdc.noaa.gov/Datasets/NARR/monolevel/"         # For temperature we extract 3 hourly data to get daily min and max
WMsq_MjMsq  = 0.0864                                                    # Convert W m^-2 into Mj m^-2 http://www.fao.org/docrep/x0490e/x0490e0i.htm

# Variables
vars_to_get = {'air.2m':'air','apcp':'apcp','rhum.2m':'rhum','uwnd.10m':'uwnd','vwnd.10m':'vwnd','dswrf':'dswrf','uswrf.sfc':'uswrf'}
# Maximum number of cpus to use at a time
max_threads = multiprocessing.cpu_count() - 1

# Date for file names
strt_date   = datetime.date(START_YR,1,1)
end_date    = datetime.date(END_YR,12,31)

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-t','--tag',help='Project name',default='OpenLands_LS')
args   = vars(parser.parse_args())

# Directories
base_dir    = os.sep.join(os.path.dirname(__file__).split(os.sep)[:-3])
data_dir    = base_dir+os.sep+'Data'+os.sep+'NETCDF'+os.sep+'narr_download'+os.sep
out_dir     = base_dir+os.sep+'EPIC'+os.sep+args['tag']+os.sep
epic_dly    = out_dir+os.sep+'daily'+os.sep
epic_mon    = out_dir+os.sep+'monthly'+os.sep

# Create directories
util.make_dir_if_missing(data_dir)
util.make_dir_if_missing(out_dir)
util.make_dir_if_missing(epic_dly)
util.make_dir_if_missing(epic_mon)

# Logging
LOG_FILENAME   = out_dir+os.sep+'Log_'+TAG+'.txt'
logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO,\
                    format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s',\
                    datefmt="%Y-%m-%d %H:%M:%S") # Logging levels are DEBUG, INFO, WARNING, ERROR, and CRITICAL

# Check if we want to do just a single site
if(DO_SITE):
    LAT_BOUNDS[0] = LAT_BOUNDS[1] = SITE_LAT
    LON_BOUNDS[0] = LON_BOUNDS[1] = SITE_LON



      
