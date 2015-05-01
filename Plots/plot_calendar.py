import pandas, pdb, os, csv, datetime, numpy, brewer2mpl
from dbfpy import dbf
import matplotlib.pyplot as plt
import matplotlib.colorbar as cbar
from dateutil import rrule
import matplotlib
import calendar

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
    bmap   = brewer2mpl.get_map('BrBG','diverging',11)
    return bmap.mpl_colors

###############################################################################
#
#
#
#
###############################################################################
def dbf_to_csv(file_name):
    if file_name.endswith('.dbf'):
        #logging.info("Converting %s to csv" % file_name)
        
        csv_fn = file_name[:-4]+ '.csv'
        
        with open(csv_fn,'wb') as csvfile:
            in_db = dbf.Dbf(file_name)
            out_csv = csv.writer(csvfile)
            names = []
            for field in in_db.header.fields:
                names.append(field.name)
            out_csv.writerow(names)
            for rec in in_db:
                out_csv.writerow(rec.fieldData)
            in_db.close()
    else:
        pass
        #logging.info("\tFilename does not end with .dbf")

    return csv_fn

base_dir = 'C:/Users/ritvik/Documents/PhD/Projects/Lake_States/Code/Python/Plots/FARS2010/'
dbf_fl   = base_dir+os.sep+'accident.dbf' 
csv_fl   = dbf_fl[:-4]+'.csv'

if(os.path.exists(csv_fl)):
    pass
else:
    csv_fl   = dbf_to_csv(dbf_fl)
    



def draw_calendar(df,horz):
    for i in range(len(df.index)):
        if(df[col_name][i] > 0):
            cur_wk = datetime.date(df.YEAR[i],df.MONTH[i],df.DAY[i]).isocalendar()[1]
            cur_yr = datetime.date(df.YEAR[i],df.MONTH[i],df.DAY[i]).isocalendar()[0]
            if(cur_yr < df.YEAR[i]):
                cur_wk = 0

            day_of_week = df.index[i].weekday()

            val = float((df[col_name][i]-min_val)/float(max_val-min_val))

            if(horz):
                rect1 = matplotlib.patches.Rectangle((cur_wk,day_of_week), 1, 1, color = color_list[int(val*color_len)-1])                
            else:
                rect1 = matplotlib.patches.Rectangle((day_of_week,cur_wk), 1, 1, color = color_list[int(val*color_len)-1])                
            ax.add_patch(rect1)
       

def draw_month_boundary(df,horz):
    month_seq = rrule.rrule(rrule.MONTHLY,dtstart=df.index[0],until=df.index[len(df.index)-1])
    for mon in month_seq:
        num_days = calendar.monthrange(mon.year,mon.month)[1]
        cur_wk = datetime.date(mon.year,mon.month,num_days).isocalendar()[1]
        day_of_week = datetime.date(mon.year,mon.month,num_days).weekday()
        if(horz):
            plt.plot([cur_wk+1,cur_wk+1],[0,day_of_week+1], 'w-', lw=1)
        else:
            plt.plot([0,day_of_week+1],[cur_wk+1,cur_wk+1], 'w-', lw=1)

        if (day_of_week != 6):
            if(horz):
                plt.plot([cur_wk+1,cur_wk],[day_of_week+1,day_of_week+1],'w-', lw=1)
                plt.plot([cur_wk,cur_wk],[day_of_week+1,7],'w-', lw=1)
            else:
                plt.plot([day_of_week+1,day_of_week+1],[cur_wk+1,cur_wk],'w-', lw=1)
                plt.plot([day_of_week+1,7],[cur_wk,cur_wk],'w-', lw=1)

if __name__ == '__main__':
    col_name       = 'VE_TOTAL'
    df             = pandas.read_csv(csv_fl)
    df             = df.groupby(['YEAR','MONTH','DAY']).sum()[col_name].reset_index()
    df['datetime'] = df[['YEAR', 'MONTH', 'DAY']].apply(lambda s : datetime.datetime(*s),axis=1)
    df             = df.set_index('datetime')

    # Span of values, if not specified
    max_val = max(df[col_name])
    min_val = min(df[col_name])
    span    = max_val - min_val

    color_list = get_colors()
    color_len  = len(color_list)

    # Find number of weeks
    start_date = df.index[0]
    end_date   = df.index[len(df.index)-1]
    num_weeks  = numpy.ceil((df.index[len(df.index)-1]-df.index[0])/(numpy.timedelta64(1,'W')))+1


    # Draw blank figure
    fig = plt.figure(dpi=400)
    ax  = fig.add_subplot(111)
    plt.xlim(0,7)
    plt.ylim(num_weeks,0)
    ###plt.axis('off')
    plt.axes().set_aspect('equal')
    ax.xaxis.tick_top()

    draw_calendar(df,horz=False)
    draw_month_boundary(df,horz=False)

    plt.show()
    plt.close()