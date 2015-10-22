import os, sys, logging, errno, multiprocessing, ast
from ConfigParser import SafeConfigParser

# Parse config file
parser = SafeConfigParser()
parser.read('../config_EPIC.txt')

###############################################################################
# User modifiable values
#
#
###############################################################################
MAX           = 100000.0                             # Maximum distance between any two points
NARR_RES      = 20.0                                 # NARR resolution (approx) at higher latitudes
M2_TO_HA      = 0.0001
RECL_RAS      = 'recl_'
MOSAIC_RAS    = 'mosaic_ras'
TAG           = parser.get('PROJECT','SEMF_TAG')     # Tag of SEIMF folder
SITELIST      = parser.get('PARAMETERS','SITELIST')
year          = parser.getint('PROJECT','YEAR')
EPIC_DLY      = parser.get('PARAMETERS','EPIC_DLY')
SLLIST        = parser.get('PARAMETERS','SLLIST')
EPICRUN       = parser.get('PARAMETERS','EPICRUN')
SOIL_DATA     = parser.get('PARAMETERS','SOIL_DATA')
SITES         = parser.get('PARAMETERS','SITES')
site_fl_line1 = parser.get('PARAMETERS','site_fl_line1')
site_fl_line3 = parser.get('PARAMETERS','site_fl_line3')
missing_soils = parser.get('PARAMETERS','missing_soils')

OUT_TAG  = parser.get('PROJECT','OUT_TAG')
EPIC_files = parser.get('PROJECT','EPIC_files')
list_st  = ast.literal_eval(parser.get('PROJECT','LIST_STATES'))
out_dir  = parser.get('PATHS', 'out_dir') + os.sep
epic_dir = out_dir + os.sep + parser.get('PROJECT','project_name') + os.sep
sims_dir = epic_dir + os.sep + parser.get('PROJECT', 'EPIC_dat') + os.sep + OUT_TAG # Directory containing .DAT files e.g. EPICRUN.dat
temp_dir = epic_dir + os.sep + parser.get('PATHS', 'sims_dir') # Directory containing template
site_dir = epic_dir + os.sep + 'inputs' + os.sep + OUT_TAG + os.sep + SITES + os.sep
mgt_dir  = epic_dir + os.sep + 'inputs' + os.sep + OUT_TAG + os.sep # Directory in which EPIC inputs (mgt, soils, weather etc.) are kept
run_dir  = epic_dir + os.sep + EPIC_files + os.sep + OUT_TAG # Directory in which epic.exe is run
out_dir  = epic_dir + os.sep + parser.get('PROJECT', 'SEMF_TAG') + os.sep + OUT_TAG + os.sep
log_dir  = epic_dir + os.sep + parser.get('PROJECT', 'LOGS') + os.sep + OUT_TAG + os.sep

# EPIC simulation specific values
EPIC_EXE    = parser.get('RUN_EPIC', 'EPIC_EXE')
EPICOUT_FLS = ast.literal_eval(parser.get('RUN_EPIC', 'EPICOUT_FLS'))
opt_rundir  = parser.get('RUN_EPIC', 'opt_rundir')
opt_epicrun = parser.get('RUN_EPIC', 'opt_epicrun')
opt_tag     = parser.get('RUN_EPIC', 'opt_tag')
opt_numpkgs = parser.getint('RUN_EPIC', 'opt_numpkgs')
opt_outdir  = parser.get('RUN_EPIC', 'opt_outdir')

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

    return d

# Create directories
make_dir_if_missing(epic_dir)
make_dir_if_missing(site_dir)
make_dir_if_missing(sims_dir)
make_dir_if_missing(log_dir)

# Logging
LOG_FILENAME = log_dir + os.sep + 'Log_' + TAG + '_' + OUT_TAG + '.txt'
logging.basicConfig(filename = LOG_FILENAME, level=logging.INFO,\
                    format='%(asctime)s    %(levelname)s %(module)s - %(funcName)s: %(message)s',\
                    datefmt="%Y-%m-%d %H:%M:%S") # Logging levels are DEBUG, INFO, WARNING, ERROR, and CRITICAL
  