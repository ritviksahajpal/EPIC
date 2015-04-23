import brewer2mpl, os
from math import ceil
from matplotlib import rcParams

from constants import *

def make_dir_if_missing(d):
    """
    Create directory if missing
    input:
        d: directory to create
    """        
    if not os.path.exists(d):
        os.makedirs(d)

def roundup(x, num):
    return int(ceil(x / num)) * num

def set_matplotlib_params():
    """
    Set matplotlib defaults to nicer values
    """            
    # rcParams dict
    rcParams['mathtext.default'] ='regular'
    rcParams['axes.labelsize']   = constants.FONT_SIZE
    rcParams['xtick.labelsize']  = constants.FONT_SIZE
    rcParams['ytick.labelsize']  = constants.FONT_SIZE
    rcParams['legend.fontsize']  = constants.FONT_SIZE
    rcParams['font.family']      = 'sans-serif'
    rcParams['font.serif']       = ['Helvetica']
    rcParams['figure.figsize']   = 4.2, 4.2
    rcParams['legend.numpoints'] = 1

def get_colors():    
    """
    Get colorbrewer colors, which are nicer
    """            
    bmap   = brewer2mpl.get_map('Accent','qualitative',6)
    return bmap.mpl_colors

def simple_axis(ax):
    """
    Remove spines from top and right, set max value of y-axis
    """            
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

def plot_soil_param(ax, plt):
    """
    Plot soil temperature for different sites, depths
    input:
        plt: matplotlib object
        leg_labels: Name of legend entries
        file_name: output file name for image
    """   
    simple_axis(ax) # Simple axis, no axis on top and right of plot    
    ax.set_ylabel('')    
    ax.set_xlabel('')    


