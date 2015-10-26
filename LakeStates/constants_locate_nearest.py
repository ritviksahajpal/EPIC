import os, sys, logging, errno, multiprocessing, ast
from ConfigParser import SafeConfigParser

# Parse config file
parser = SafeConfigParser()
parser.read('../config_EPIC.txt')

MAX           = 100000.0                             # Maximum distance between any two points
TAG           = parser.get('PROJECT','SEMF_TAG')          # Tag of SEIMF folder
EPIC_DLY      = parser.get('PARAMETERS','EPIC_DLY')
base_dir      = parser.get('PATHS','base_dir')+os.sep
epic_dir      = base_dir + os.sep + 'EPIC' + os.sep + parser.get('PROJECT', 'project_name') + os.sep + \
                parser.get('PROJECT', 'EPIC_dat') + os.sep + parser.get('PROJECT', 'OUT_TAG') + os.sep
site_lat_lon  = ast.literal_eval(parser.get('PARAMETERS','site_loc'))