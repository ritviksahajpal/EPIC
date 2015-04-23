from math import exp, log, pow, ceil
import pdb, pandas, csv, itertools, random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import matplotlib.cm as cm
import matplotlib.dates as mdates
import ast

# Import project code
import constants
import utils

if __name__ == '__main__':        
    if(len(constants.SITE_NAMES) > constants.NUM_PLOTS_COLS):
        ncol = constants.NUM_PLOTS_COLS
    else:
        ncol = len(constants.SITE_NAMES)    
    nrow     = len(constants.SITE_NAMES)/ncol + len(constants.SITE_NAMES)%ncol

    # Read in data
    xl = pd.ExcelFile(constants.base_dir+constants.soil_dir+constants.SOIL_FILE)
    df = xl.parse(constants.SHEET_NAME,skiprows=1,parse_dates=['date'])

    # Change the data columns from object to numeric
    for j in constants.DATA_COLS:
        df[j] = df[j].convert_objects(convert_numeric=True)
        df[j] = df[j].convert_objects(convert_numeric=True)
    
    # Convert the trt column to all lower case
    df.trt = df.trt.str.lower()
    # Exclude fertilized plots
    df = df[~df.trt.isin([u'pf',u'wf'])]
    # Change all rep's to strings
    ###df['rep'] = df['rep'].astype(str).tolist()
    # Change non 'pre' rep's to nonpre
    ###df.loc[df['rep'] != 'pre', 'rep'] = 'nonpre'    
    # Convert all site names:
    df.site.replace(constants.SITE_NAMES,inplace=True)
    # Get subset of sites we want to draw
    df     = df[df.site.isin(constants.SITE_NAMES.values())]
    
    for dat in constants.DATA_COLS:
        print dat        
        df_pvt = df.pivot_table(index=['site','date'],columns='trt',values=dat,aggfunc='mean',fill_value=0.0)
        df_err = df.pivot_table(index=['site','date'],columns='trt',values=dat,aggfunc=np.std,fill_value=0.0)
        df_pvt.reset_index(inplace=True)
        df_err.reset_index(inplace=True)

        df_pvt.to_csv(constants.base_dir+constants.soil_dir+'df_pvt.csv')
        # Determine maximum value on y axis
        y_max = utils.roundup(df[dat].max(),10.0)
            
        # Start plotting                               
        utils.set_matplotlib_params()
        colors = utils.get_colors()
              
        # Set up the axes and figure
        fig, axis = plt.subplots(nrows=nrow, ncols=ncol, figsize=(5*ncol,5*nrow))

        ctr       = [(x, y) for x in np.arange(nrow) for y in np.arange(ncol)]
        site_ctr  = 0
        
        for i in ctr:
            if(nrow > 1):
                ax = axis[i[0],i[1]]
            else:
                ax = axis[site_ctr]
            
            if(site_ctr >= len(constants.SITE_NAMES)):
                ax.axis('off')
                continue
            
            df_plot     = df_pvt[df_pvt.site==constants.SITE_NAMES.values()[site_ctr]]    
            df_err_plot = df_err[df_err.site==constants.SITE_NAMES.values()[site_ctr]]
            
                    
            col_ctr = 0
            markers = ['o','s','^']
            for l in constants.leg_labels:                        
                ts = pd.Series(df_plot[l].values,index=df_plot['date'])
                tr = pd.Series(df_err_plot[l].values,index=df_err_plot['date'])    
                 
                
                ts.plot(ax=ax, ylim=(-5,y_max), xticks=ts.index, yticks=ts.tolist(),\
                        yerr=tr.tolist(), color=colors[col_ctr], linestyle='', marker=markers[col_ctr],alpha=0.6)

                utils.plot_soil_param(ax, plt)
                ax.yaxis.set_major_locator(tkr.MaxNLocator(constants.NUM_YAXIS_TICKS))
                ax.xaxis.set_major_locator(tkr.MaxNLocator(constants.NUM_XAXIS_TICKS))
                ax.set_title(constants.SITE_NAMES.values()[site_ctr], fontsize=constants.FONT_SIZE)
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
                 
                col_ctr += 1
            
            # Draw legend for 1st plot
            if(site_ctr == 0):
                leg = ax.legend(constants.leg_labels,loc='upper left', fancybox=None)
                leg.get_frame().set_linewidth(0.0)
                leg.get_frame().set_alpha(0.8)    
                
                           
            site_ctr += 1
                            
        if(dat == 'NH4'):
            y_lab = r'NH$_4$$^+$ (mg kg$^-$$^1$)'
        elif(dat == 'NO3'):
            y_lab = r'NO$_3$$^-$ (mg kg$^-$$^1$)'
        else:
            y_lab = ''
            
        # Common y axis label
        fig.text(0.06, 0.5, y_lab, ha='center', va='center', rotation='vertical', fontsize=constants.FONT_SIZE+4)
        # Separate out the plots
        fig.subplots_adjust(hspace=constants.PLOT_HSEP)    

        plt.savefig(constants.base_dir+constants.soil_dir+os.sep+dat+'.png', bbox_inches='tight', dpi=constants.DPI)
        plt.close()