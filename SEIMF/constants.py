import os, sys, logging, errno, multiprocessing, ast
from ConfigParser import SafeConfigParser

# Parse config file
parser = SafeConfigParser()
parser.read('config_SEIMF.txt')

###############################################################################
# User modifiable values
#
#
###############################################################################
TAG           = parser.get('PROJECT','TAG')          # Tag of SEIMF folder
SITELIST      = parser.get('PARAMETERS','SITELIST')
year          = parser.getint('PARAMETERS','YEAR')  

list_st       = ast.literal_eval(parser.get('PROJECT','LIST_STATES'))
base_dir      = parser.get('PATHS','base_dir')+os.sep
epic_dir      = base_dir+os.sep+'EPIC'+os.sep+parser.get('PROJECT','project_name')+os.sep

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

# Logging
LOG_FILENAME   = epic_dir+os.sep+'Log_'+TAG+'.txt'
logging.basicConfig(filename = LOG_FILENAME, level=logging.INFO,\
                    format='%(asctime)s    %(levelname)s %(module)s - %(funcName)s: %(message)s',\
                    datefmt="%Y-%m-%d %H:%M:%S") # Logging levels are DEBUG, INFO, WARNING, ERROR, and CRITICAL
  