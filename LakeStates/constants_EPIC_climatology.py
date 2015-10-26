import os, errno
from ConfigParser import SafeConfigParser

# Parse config file
parser = SafeConfigParser()
parser.read('config_EPIC_climatology.txt')

TAG           = parser.get('PROJECT','TAG')          # Tag of SEIMF folder
start_yr      = parser.getint('PARAMETERS','START_YR')
until_yr      = parser.getint('PARAMETERS','UNTIL_YR')

base_dir      = parser.get('PATHS','base_dir')+os.sep
epic_dir      = base_dir + os.sep + 'EPIC' + os.sep + parser.get('PROJECT', 'project_name') + os.sep + \
                parser.get('PROJECT', 'EPIC_dat') + parser.get('PROJECT', 'OUT_TAG') + os.sep
wth_dir       = epic_dir+os.sep+'daily'
out_dir       = epic_dir+os.sep+'climatology_'+str(start_yr)+'_'+str(until_yr)

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

make_dir_if_missing(out_dir)