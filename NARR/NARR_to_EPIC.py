###############################################################################
# create_EPIC_weather_files.py
# email: ritvik@umd.edu, 24th March, 2015.
#
# Convert downloaded data to EPIC compatible weather files.
###############################################################################
import constants, util, logging, os, pandas, datetime, pdb, multiprocessing
from dateutil.rrule import rrule, DAILY, YEARLY
from dateutil.relativedelta import *

# For each grid cell (y_x) process the output data to create an EPIC weather file
###############################################################################
# NARR_to_EPIC
# Convert NARR text file into a EPIC weather files
# 
###############################################################################
def NARR_to_EPIC(vals):
    lat,lon = vals
    # Output pandas frame into EPIC weather file
    out_fl   = constants.epic_dly+os.sep+str(lat)+'_'+str(lon)+'.txt'

    if not(os.path.isfile(out_fl)):
        logging.info(out_fl) 
        # List all years for which we will create EPIC file
        lst_yrs     = rrule(YEARLY, dtstart=constants.strt_date, until=constants.end_date)

        # Create pandas data frame, fill with 0.0s, for 1st year.
        epic_df = pandas.DataFrame(index=pandas.date_range(constants.strt_date,constants.end_date),\
                                   columns=[constants.vars_to_get.keys()])
        epic_out = open(out_fl,'w')

        # Loop across years
        for idx_yr in range(lst_yrs.count()):		
            cur_strt_date  = datetime.date(lst_yrs[idx_yr].year,1,1)
            cur_end_date   = datetime.date(lst_yrs[idx_yr].year,12,31)
            cur_date_range = pandas.date_range(cur_strt_date,cur_end_date)

            tmp_df         = pandas.DataFrame(index=cur_date_range,columns=[constants.vars_to_get.keys()])
            tmp_df.fillna(0.0,inplace=True)
            # Loop across variables
            for cur_var in constants.vars_to_get.keys():
                e_fl           = open(constants.out_dir+os.sep+'Data'+os.sep+cur_var+os.sep+str(lst_yrs[idx_yr].year)+\
                                      os.sep+str(lat)+'_'+str(lon)+'.txt')
                epic_vars      = filter(None,e_fl.readlines()[0].strip().split("'"))

                if cur_var == 'air.2m':
                    epic_min_tmp     = util.chunks(epic_vars,8,True)
                    epic_max_tmp     = util.chunks(epic_vars,8,False)                    

                    tmp_df[cur_var] = pandas.Series(epic_min_tmp,index=cur_date_range)
                    tmp_df[cur_var] = tmp_df[cur_var].map(lambda x:float(x)+constants.K_To_C)

                    tmp_df['tmax']  = pandas.Series(epic_max_tmp,index=cur_date_range)
                    tmp_df['tmax']  = tmp_df['tmax'].map(lambda x:float(x)+constants.K_To_C)
                    tmp_df['tmin']  = tmp_df['air.2m'] 
                else:
                    tmp_df[cur_var] = pandas.Series(epic_vars,index=cur_date_range)
                    tmp_df[cur_var] = tmp_df[cur_var].map(lambda x:float(x))
        
            # Get into right units
            tmp_df['wnd']      = pandas.Series(tmp_df['uwnd.10m'].astype(float)**2.0+\
                                                tmp_df['vwnd.10m'].astype(float)**2.0,index=tmp_df.index)
            tmp_df['wnd']      = tmp_df['wnd']**0.5
            tmp_df['rhum.2m']  = tmp_df['rhum.2m'].map(lambda x:float(x)/100.0)
            tmp_df['swr_diff'] = pandas.Series(tmp_df['dswrf']-tmp_df['uswrf.sfc'],index=tmp_df.index)
            tmp_df['srad']     = tmp_df['swr_diff'].map(lambda x:constants.WMsq_MjMsq*x)
            tmp_df['year']     = tmp_df.index.year
            tmp_df['month']    = tmp_df.index.month
            tmp_df['day']      = tmp_df.index.day
            epic_df            = epic_df.combine_first(tmp_df)
        # Output dataframe to text file with right formatting
        for index, row in epic_df.iterrows():
            epic_out.write(('%6d%4d%4d'+6*'%6.2f'+'\n') %
                        (row['year'],row['month'],row['day'],
                         row['srad'],row['tmax'],row['tmin'],
                         row['apcp'],row['rhum.2m'],row['wnd']))	
        epic_out.close()
    else:
        logging.info('File exists: '+out_fl) 

###############################################################################
# parallelize_NARR_to_EPIC
# Iterate/Parallelize NARR text file conversion to EPIC files
#
###############################################################################
def parallelize_NARR_to_EPIC():
    # Read EPIC weather list file
    epic_wth_list = open(constants.out_dir+constants.EPIC_DLY,'r').readlines()

    if constants.DO_PARALLEL:
        lat_vals = [int(ln.split('/')[1].split('.')[0].split('_')[0]) for ln in epic_wth_list]
        lon_vals = [int(ln.split('/')[1].split('.')[0].split('_')[1]) for ln in epic_wth_list]

        pool = multiprocessing.Pool(constants.max_threads)
        pool.map(NARR_to_EPIC,zip(lat_vals,lon_vals))
        pool.close()
        pool.join()
    else:
        for line in epic_wth_list:
            lat_val = int(line.split('/')[1].split('.')[0].split('_')[0])
            lon_val = int(line.split('/')[1].split('.')[0].split('_')[1])
            NARR_to_EPIC((lat_val,lon_val))
    logging.info('Done NARR_to_EPIC!')

if __name__ == '__main__':
    parallelize_NARR_to_EPIC()