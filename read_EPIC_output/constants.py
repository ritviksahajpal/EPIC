import os, sys, logging, errno, multiprocessing, ast
from ConfigParser import SafeConfigParser

# Parse config file
parser = SafeConfigParser()
parser.read('config_EPIC_output.txt')

###############################################################################
# Constants
#
#
###############################################################################
SKIP = 10

###############################################################################
# User modifiable values
#
#
###############################################################################
PROJECT_NAME  = parser.get('PROJECT','project_name')
TAG           = parser.get('PROJECT','TAG')
START_YR      = parser.get('PARAMETERS','START_YR')                
END_YR        = parser.get('PARAMETERS','END_YR')                 
SIMULATIONS   = parser.get('PARAMETERS','SIMULATIONS')
EPIC_OUTPUT   = parser.get('PARAMETERS','EPIC_OUTPUT')
ACM_PARAMS    = ast.literal_eval(parser.get('PARAMETERS','ACM_PARAMS'))
ACY_PARAMS    = ast.literal_eval(parser.get('PARAMETERS','ACY_PARAMS'))
DGN_PARAMS    = ast.literal_eval(parser.get('PARAMETERS','DGN_PARAMS'))
GET_PARAMS    = ast.literal_eval(parser.get('PARAMETERS','GET_PARAMS'))

base_dir = parser.get('PATHS','base_dir') + os.sep
epic_dir = base_dir + os.sep + 'EPIC' + os.sep + PROJECT_NAME + os.sep
sims_dir = epic_dir + os.sep + SIMULATIONS + os.sep + EPIC_OUTPUT
anly_dir = epic_dir + os.sep + 'analysis' + os.sep

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
make_dir_if_missing(epic_dir)
make_dir_if_missing(sims_dir)
make_dir_if_missing(anly_dir)

# Logging
LOG_FILENAME   = epic_dir+os.sep+'Log_'+TAG+'.txt'
logging.basicConfig(filename = LOG_FILENAME, level=logging.INFO,\
                    format='%(asctime)s    %(levelname)s %(module)s - %(funcName)s: %(message)s',\
                    datefmt="%Y-%m-%d %H:%M:%S") # Logging levels are DEBUG, INFO, WARNING, ERROR, and CRITICAL
  