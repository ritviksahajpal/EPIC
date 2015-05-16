import pandas,pdb,os,csv,datetime,numpy,palettable,matplotlib,calendar
import matplotlib.pyplot as plt
import matplotlib.colorbar as cbar
from matplotlib import rcParams
from matplotlib.ticker import MaxNLocator
from dateutil import rrule
 
def set_matplotlib_params():
    """
    Set matplotlib defaults to nicer values
    """            
    # rcParams dict
    rcParams['mathtext.default'] ='regular'
    rcParams['axes.labelsize']   = 11
    rcParams['xtick.labelsize']  = 11
    rcParams['ytick.labelsize']  = 11
    rcParams['legend.fontsize']  = 11
    rcParams['font.family']      = 'sans-serif'
    rcParams['font.serif']       = ['Helvetica']
    rcParams['figure.figsize']   = 7.3, 4.2
   
###############################################################################
# get_colors
#
#
#
###############################################################################
def get_colors():    
    """
    Get palettable colors, which are nicer
    """            
    bmap=palettable.colorbrewer.sequential.BuPu_9.mpl_colors
    return bmap
 
###############################################################################
# draw_calendar
#
#
#
###############################################################################
def draw_calendar(ax,df,col_name,horz=False):
    for i in range(len(df.index)):
        if(df[col_name][i] > 0):
            max_val = max(df[col_name])
            min_val = min(df[col_name])
            color_list = get_colors()
            color_len  = len(color_list)

            cur_wk = datetime.date(df.YEAR[i],df.MONTH[i],df.DAY[i]).isocalendar()[1]
            cur_yr = datetime.date(df.YEAR[i],df.MONTH[i],df.DAY[i]).isocalendar()[0]

            if((cur_yr < df.YEAR[i]) and (df.DAY[i]<7)):
                cur_wk = 0
            if(cur_yr>df.YEAR[i]):
                cur_wk = 53
            day_of_week = df.index[i].weekday()
 
            #normalise each data point to val - note added a very small amount
            #to data range, so that we never get exactly 1.0
            val = float((df[col_name][i]-min_val)/float(max_val-min_val + 0.000001))
            if(horz):
                rect = matplotlib.patches.Rectangle((cur_wk,day_of_week), 1, 1, color = color_list[int(val*color_len)])                
            else:
                rect = matplotlib.patches.Rectangle((day_of_week,cur_wk), 1, 1, color = color_list[int(val*color_len)],label='a')                
 
            ax.add_patch(rect)
       
###############################################################################
# draw_daily_lines
#
#
#
###############################################################################
def draw_daily_lines(ax,df,num_weeks,horz=False):
    clr = 'w' # White line
    wth = 0.5 
    stl = '-'
    adj = 0.08

    # Draw calendar grid 
    # Subtract adj so that lines are 'lined up' nicely
    for i in range(int(num_weeks)):
        ax.plot([0,7],[i-adj,i-adj],color=clr,linestyle=stl,lw=wth)
    
    for j in range(7):
        ax.plot([j-adj,j-adj],[0,num_weeks],color=clr,linestyle=stl,lw=wth)    
 
###############################################################################
# draw_month_boundary
# Separate out months from each other by a thick white line
#
#
###############################################################################
def draw_month_boundary(ax,df,horz=False):
    clr = 'w'  # White line
    wth = 1.25 # Thicker line as compared to daily lines
    stl = '-'
    adj = 0.08

    month_seq = rrule.rrule(rrule.MONTHLY,dtstart=df.index[0],until=df.index[len(df.index)-1])
    for mon in month_seq:
        num_days = calendar.monthrange(mon.year,mon.month)[1]
        cur_wk = datetime.date(mon.year,mon.month,num_days).isocalendar()[1]
        cur_yr = datetime.date(mon.year,mon.month,num_days).isocalendar()[0]
        day_of_week = datetime.date(mon.year,mon.month,num_days).weekday()
 
        # No need to draw anything after the 12th month
        if(cur_yr == mon.year and (mon.month <> 12)):               
            if(horz):
                ax.plot([cur_wk+1,cur_wk+1],[0,day_of_week+1],color=clr,linestyle=stl,lw=wth)
            else:
                ax.plot([0,day_of_week+1],[cur_wk+1-adj,cur_wk+1-adj],color=clr,linestyle=stl,lw=wth)
 
            if (day_of_week != 6):
                if(horz):
                    ax.plot([cur_wk+1,cur_wk],[day_of_week+1,day_of_week+1],color=clr,linestyle=stl,lw=wth) # Parallel to X-Axis
                    ax.plot([cur_wk,cur_wk],[day_of_week+1,7],color=clr,linestyle=stl,lw=wth)
                else:
                    ax.plot([day_of_week+1-adj,day_of_week+1-adj],[cur_wk+1,cur_wk],color=clr,linestyle=stl,lw=wth) # Parallel to Y-axis
                    ax.plot([day_of_week+1,7],[cur_wk-adj,cur_wk-adj],color=clr,linestyle=stl,lw=wth)
 
###############################################################################
#
#
#
#
###############################################################################
def plot_epic_dgn():
    col_name       = 'DN'   
    horz           = False # Whether to draw the plot horizontally or not
 
    df             = pandas.read_csv('94.DGN',skiprows=10,delim_whitespace=True,usecols=['Y','M','D','BIOM','NMN','DN'])    
    df.rename(columns={'Y':'YEAR','M':'MONTH','D':'DAY'}, inplace=True)
 
    df['datetime'] = df[['YEAR', 'MONTH', 'DAY']].apply(lambda s : datetime.datetime(*s),axis=1)
    df             = df.set_index('datetime')
 
    num_yrs = len(df['YEAR'].unique())
    max_val = max(df[col_name])
    min_val = min(df[col_name])
 
    # Draw blank figure
    fig = plt.figure()
    set_matplotlib_params()
    plt.subplots_adjust(hspace=0.3)
    #plt.axis('off')       
    plt.axes().set_aspect('equal')
 
    idx = 0
    for i in df['YEAR'].unique():  
        # Get data for year i      
        sub_df = df[df['YEAR']==i]   
 
        start_date = sub_df.index[0]
        end_date   = sub_df.index[len(sub_df.index)-1]
        diff = end_date - start_date
        diff = numpy.timedelta64(diff)
        # Maximum number of weeks (including partials) in a year is 54
        num_weeks  = numpy.ceil(diff/(numpy.timedelta64(1,'W')))+2    
        
        if(horz):
            ax  = plt.subplot2grid((num_yrs+1,9),(3,idx),colspan=5,rowspan=1)
        else:
            ax  = plt.subplot2grid((9,num_yrs+1),(3,idx),rowspan=5,colspan=1)            
        ax.xaxis.tick_top()
 
        ax.axes.get_xaxis().set_ticks([])
        ax.axes.get_yaxis().set_ticks([])
        ax.axis('off')
        ax.set_title(str(i),fontsize=12)
 
        if (horz):
            plt.xlim(0,num_weeks)
            plt.ylim(0,7)
        else:
            plt.xlim(0,7)
            plt.ylim(num_weeks,0)

        if(i == max(df['YEAR'].unique())):
            plt.text(8,3,'Jan',fontsize=10)
            plt.text(8,8,'Feb',fontsize=10)
            plt.text(8,12,'Mar',fontsize=10)
            plt.text(8,16,'Apr',fontsize=10)
            plt.text(8,21,'May',fontsize=10)
            plt.text(8,25,'Jun',fontsize=10)
            plt.text(8,29,'Jul',fontsize=10)
            plt.text(8,34,'Aug',fontsize=10)
            plt.text(8,38,'Sept',fontsize=10)
            plt.text(8,42,'Oct',fontsize=10)
            plt.text(8,47,'Nov',fontsize=10)
            plt.text(8,51,'Dec',fontsize=10)
 
        draw_calendar(ax,sub_df,col_name,horz)      # Draw the individual rectangles
        draw_daily_lines(ax,sub_df,num_weeks,horz) # Draw separation between days
        draw_month_boundary(ax,sub_df,horz)         # Draw separation between weeks
        print idx, i
        idx += 1
        
    # plot an overall colorbar type legend    
    # You can change the boundaries kwarg to either make the scale look less boxy (increase 10)
    # or to get different values on the tick marks, or even omit it altogether to let
    ax_colorbar = plt.subplot2grid((9,num_yrs+1), (8,1),rowspan=1,colspan=num_yrs-1)   
    mappableObject = matplotlib.cm.ScalarMappable(cmap = palettable.colorbrewer.sequential.BuPu_9.mpl_colormap)
    mappableObject.set_array(numpy.array(df[col_name]))
    col_bar = fig.colorbar(mappableObject,cax=ax_colorbar,orientation='horizontal',\
                           boundaries=numpy.arange(min_val,max_val,(max_val-min_val)/100))
    col_bar.ax.tick_params(labelsize=8) 
    ###col_bar.set_label(col_name)
    ###ax_colorbar.set_title(col_name + ' color mapping')        
   
    #draw the top overall graph
    ax0     = plt.subplot2grid((9,num_yrs+1), (0,0),rowspan=3,colspan=num_yrs)
    x_axis  = numpy.arange(0.325,num_yrs+1,1.1)
    bar_val = df[col_name].groupby(df['YEAR']).mean()
    err_val = df[col_name].groupby(df['YEAR']).std()
    ax0.bar(x_axis,bar_val,yerr=err_val,linewidth=0,width=0.25,color='g',
            error_kw=dict(ecolor='gray', lw=1))
    ax0.axes.get_xaxis().set_ticks([])
    ax0.spines['top'].set_visible(False)
    ax0.spines['right'].set_visible(False)
    ax0.yaxis.set_major_locator(MaxNLocator(5))
    plt.ylabel(col_name+' (kg/ha)')
    #ax0.axes.get_yaxis().set_ticks([])
    ax0.spines['left'].set_visible(False)
    plt.gca().yaxis.grid(True)	
    plt.tight_layout(w_pad=0.0)
    plt.savefig('C:\\Users\\ritvik\\Documents\\PhD\\Projects\\Lake_States\\QZDN94.png',dpi=900,frameon=False)
    plt.close()

if __name__ == '__main__':
    plot_epic_dgn()