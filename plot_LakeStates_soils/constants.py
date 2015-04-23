from ConfigParser import SafeConfigParser

# Parse config file
parser = SafeConfigParser()
parser.read('config_plot_site_soils.txt')

# General constants
base_dir   = parser.get('PATHS','base_dir')+os.sep
soil_dir   = parser.get('PATHS','soil_dir')+os.sep
SITE_NAMES = {'ES':'Escanaba','RH':'Rhinelander','LC':'Lake City','ON':'Onway','SK':'Skandia','WR':'Whiskey River'}#,'GR':'Grand Rapids'}
SOIL_FILE  = parser.get('PARAMETERS','SOIL_FILE')
SHEET_NAME = parser.get('PARAMETERS','SHEET_NAME')
DATA_COLS  = ast.literal_eval(parser.get('PARAMETERS','DATA_COLS'))
leg_labels = ast.literal_eval(parser.get('PARAMETERS','leg_labels'))

# Graphics
NUM_PLOTS_COLS  = parser.getint('PARAMETERS','NUM_PLOTS_COLS') 
NUM_XAXIS_TICKS = parser.getint('PARAMETERS','NUM_XAXIS_TICKS')
NUM_YAXIS_TICKS = parser.getint('PARAMETERS','NUM_YAXIS_TICKS')
FONT_SIZE       = parser.getint('PARAMETERS','FONT_SIZE')
DPI             = parser.getint('PARAMETERS','DPI')
PLOT_HSEP       = parser.getfloat('PARAMETERS','PLOT_HSEP') # horizontal separation between plots