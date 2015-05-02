import pandas, pdb, os, csv, datetime, numpy, brewer2mpl
import matplotlib.pyplot as plt
import matplotlib.colorbar as cbar
import seaborn as sns
from dateutil import rrule
import matplotlib
import calendar

def example_plot(ax):    
    X   = numpy.linspace(-numpy.pi, numpy.pi, 256,endpoint=True)
    C,S = numpy.cos(X), numpy.sin(X)
    ax.plot(X, C, color="blue", linewidth=1.0, linestyle="-")
    ax.axes.get_xaxis().set_ticks([])
    ax.axes.get_yaxis().set_ticks([])

###############################################################################
#
#
#
#
###############################################################################
def get_colors():    
    """
    Get colorbrewer colors, which are nicer
    """            
    #bmap = brewer2mpl.get_map('YlGnBu','sequential',9) #.mpl_colors
    bmap = sns.cubehelix_palette(8,start=1.0)
    return bmap

###############################################################################
#
#
#
#
###############################################################################
def draw_calendar(ax,df,horz):
    for i in range(len(df.index)):
        if(df[col_name][i] > 0):
            cur_wk = datetime.date(df.YEAR[i],df.MONTH[i],df.DAY[i]).isocalendar()[1]
            cur_yr = datetime.date(df.YEAR[i],df.MONTH[i],df.DAY[i]).isocalendar()[0]
            if((cur_yr < df.YEAR[i]) and (df.DAY[i]<7)):
                cur_wk = 0
            if(cur_yr>df.YEAR[i]):
                cur_wk = 53
            day_of_week = df.index[i].weekday()

            val = float((df[col_name][i]-min_val)/float(max_val-min_val))

            if(horz):
                rect = matplotlib.patches.Rectangle((cur_wk,day_of_week), 1, 1, color = color_list[int(val*color_len)-1])                
            else:
                rect = matplotlib.patches.Rectangle((day_of_week,cur_wk), 1, 1, color = color_list[int(val*color_len)-1])                
            #print cur_wk,day_of_week
            ax.add_patch(rect)
       

def draw_daily_lines(ax,df,horz):
    clr = 'w'
    # Draw calendar grid
    num_weeks  = numpy.ceil((sub_df.index[len(sub_df.index)-1]-sub_df.index[0])/(numpy.timedelta64(1,'W')))+2

    for i in range(int(num_weeks)):
        ax.plot([0,7],[i,i],color=clr,linestyle='-',lw=1)
    
    for j in range(7):
        ax.plot([j,j],[0,num_weeks],color=clr,linestyle='-',lw=1)    

    pass

def draw_month_boundary(ax,df,horz):
    clr = 'w'
    month_seq = rrule.rrule(rrule.MONTHLY,dtstart=df.index[0],until=df.index[len(df.index)-1])
    for mon in month_seq:
        num_days = calendar.monthrange(mon.year,mon.month)[1]
        cur_wk = datetime.date(mon.year,mon.month,num_days).isocalendar()[1]
        cur_yr = datetime.date(mon.year,mon.month,num_days).isocalendar()[0]
        day_of_week = datetime.date(mon.year,mon.month,num_days).weekday()

        if(cur_yr == mon.year and (mon.month <> 12)):               
            if(horz):
                ax.plot([cur_wk+1,cur_wk+1],[0,day_of_week+1],color=clr,linestyle='-',lw=2)
            else:
                ax.plot([0,day_of_week+1],[cur_wk+1,cur_wk+1],color=clr,linestyle='-',lw=2)

            if (day_of_week != 6):
                if(horz):
                    ax.plot([cur_wk+1,cur_wk],[day_of_week+1,day_of_week+1],color=clr,linestyle='-',lw=2) # Parallel to X-Axis
                    ax.plot([cur_wk,cur_wk],[day_of_week+1,7],color=clr,linestyle='-',lw=2)
                else:
                    ax.plot([day_of_week+1,day_of_week+1],[cur_wk+1,cur_wk],color=clr,linestyle='-',lw=2) # Parallel to Y-axis
                    ax.plot([day_of_week+1,7],[cur_wk,cur_wk],color=clr,linestyle='-',lw=2)

if __name__ == '__main__':
    col_name       = 'NMN'   
    horz           = False

    df      = pandas.read_csv('94.DGN',skiprows=10,delim_whitespace=True,usecols=['Y','M','D','BIOM','NMN','DN'])    
    df.rename(columns={'Y':'YEAR','M':'MONTH','D':'DAY'}, inplace=True)

    df['datetime'] = df[['YEAR', 'MONTH', 'DAY']].apply(lambda s : datetime.datetime(*s),axis=1)
    df             = df.set_index('datetime')

    num_yrs = len(df['YEAR'].unique())
    max_val = max(df[col_name])
    min_val = min(df[col_name])
    color_list = get_colors()
    color_len  = len(color_list)

    # Draw blank figure
    fig = plt.figure(dpi=900)
    plt.subplots_adjust(hspace=0.3)
    plt.axis('off')       
    plt.axes().set_aspect('equal')

    idx = 0
    for i in df['YEAR'].unique():        
        sub_df = df[df['YEAR']==i]

        start_date = sub_df.index[0]
        end_date   = sub_df.index[len(sub_df.index)-1]
        num_weeks  = numpy.ceil((sub_df.index[len(sub_df.index)-1]-sub_df.index[0])/(numpy.timedelta64(1,'W')))+2    
        
        if(horz):
            ax  = plt.subplot2grid((num_yrs,3),(1,idx),colspan=2,rowspan=1)
        else:
            ax  = plt.subplot2grid((3,num_yrs),(1,idx),rowspan=2,colspan=1)
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

        draw_calendar(ax,sub_df,horz)
        draw_daily_lines(ax,sub_df,horz)
        draw_month_boundary(ax,sub_df,horz)           
        print idx, i
        idx += 1

    ax0 = plt.subplot2grid((3,num_yrs), (0,0),rowspan=1,colspan=num_yrs)
    example_plot(ax0)    
    #plt.tight_layout()
    plt.savefig('C:\\Users\\ritvik\\Documents\\PhD\\Projects\\Lake_States\\aaa.png')
    plt.close()
