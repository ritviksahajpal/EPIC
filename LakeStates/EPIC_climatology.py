import pandas as pd
import pdb, calendar, glob, os
import constants_EPIC_climatology as constants

##################################################################
# multi_year_data
#
#
#
##################################################################
def multi_year_data(data, start_y, until_y):
    def leapyr(n):
        return calendar.isleap(n)

    multi_year = []
    for y in range(start_y,until_y+1):
        if leapyr(y):
            multi_year.extend(data)
        else:
            multi_year.extend(data[:59]+data[60:])
    return multi_year

##################################################################
# compute_climatology
#
#
#
##################################################################
def compute_climatology(col_num,inp_df,ix_df,new_dates):
    col_data = pd.Series(inp_df[col_num],index=ix_df)                             # Create series from column
    clg_data = col_data.groupby([col_data.index.month,col_data.index.day]).mean() # Produce climatology

    # Create new dataframe using climatology data and extending across new time period
    new_years_data = pd.Series(multi_year_data(clg_data.tolist(),constants.start_yr,constants.until_yr),index=new_dates)

    return new_years_data

##################################################################
# read_input_data
#
#
#
##################################################################
def read_input_data(fl):
    inp_df    = pd.read_csv(fl,header=None,index_col='datetime',delim_whitespace=True,
                     parse_dates={'datetime': [0,1,2]},keep_date_col=True,
                     date_parser=lambda x: pd.datetime.strptime(x, '%Y %m %d'))
    ix_df     = inp_df.index

    return inp_df,ix_df

##################################################################
# iterate_weather_files
#
#
#
##################################################################
def iterate_weather_files():
    new_dates = pd.date_range(str(constants.start_yr)+'-01-01',str(constants.until_yr)+'-12-31',freq='D')

    # Iterate through all daily weather files
    for fl in glob.iglob(os.path.join(constants.wth_dir, '*.txt')):
        print os.path.basename(fl)
        inp_df,ix_df = read_input_data(fl)

        # Create output climatology file
        frames = [compute_climatology(col_num,inp_df,ix_df,new_dates) for col_num in xrange(3,len(inp_df.columns))]
        result = pd.concat(frames,axis=1)

        # Add year, month and day columns (1st 3 columns)
        result.columns = xrange(3,len(inp_df.columns))
        result[0] = result.index.year
        result[1] = result.index.month
        result[2] = result.index.day

        comb_df   = pd.concat([inp_df,result])

        # Output to new weather file
        epic_out  = open(constants.out_dir+os.sep+os.path.basename(fl),'w')
        for index, row in comb_df.iterrows():
            epic_out.write(('%6d%4d%4d'+6*'%6.2f'+'\n') %
                        (int(row[0]),int(row[1]),int(row[2]),
                         float(row[3]),float(row[4]),float(row[5]),
                         float(row[6]),float(row[7]),float(row[8])))
        epic_out.close()

if __name__ == '__main__':
    iterate_weather_files()