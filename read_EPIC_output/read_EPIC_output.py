import constants, pandas, pdb, os, fnmatch
from datetime import datetime, timedelta

def parse_ACY(list_fls):
    for fl in list_fls:
        df      = pandas.read_csv(fl,skiprows=constants.SKIP,skipinitialspace=True,\
                                  usecols=constants.ACY_PARAMS,sep=' ')    
        time_df = df[(df.YR>=constants.START_YR) & (df.YR<=constants.END_YR)]
        time_df.groupby(lambda x: xrange.year).sum()

def parse_ANN(list_fls):
    for fl in list_fls:
        df      = pandas.read_csv(fl,skiprows=constants.SKIP,skipinitialspace=True,\
                                  usecols=constants.ANN_PARAMS,sep=' ')
        time_df = df[(df.YR>=constants.START_YR) & (df.YR<=constants.END_YR)]
        time_df.groupby(lambda x: xrange.year).sum()

def parse_DGN(list_fls):
    for fl in list_fls:
        df      = pandas.read_csv(fl,skiprows=constants.SKIP,delim_whitespace=True,usecols=constants.DGN_PARAMS,
                             parse_dates={"datetime": [0,1,2]}, index_col="datetime",
                            date_parser=lambda x: pandas.datetime.strptime(x, '%Y %m %d'))    
        time_df = df.ix[constants.START_YR:constants.END_YR]        
        print time_df.groupby(time_df.index.map(lambda x: x.year)).max()
        pdb.set_trace()



def collect_epic_output():
    epic_fl_types = constants.GET_PARAMS

    for fl_name in epic_fl_types:
        list_fls = fnmatch.filter(os.listdir(constants.sims_dir+os.sep),'*.'+fl_name)

        if(fl_name == 'DGN'):
            parse_DGN(list_fls)
        elif(fl_name == 'ACY'):
            parse_ACY(list_fls)
        elif(fl_name == 'ANN'):
            parse_ANN(list_fls)
        elif(fl_name == 'ACN'):
            parse_ACN(list_fls)

    #in_ssurgo_file = dir_name+os.sep+constants.SPATIAL+os.sep+\
    #            fnmatch.filter(os.listdir(dir_name+os.sep+constants.SPATIAL+os.sep),\
    #            'soilmu_a_*.shp')[0]
    pass

if __name__ == '__main__':
    collect_epic_output()



#print df.index
#print df.head()
pdb.set_trace()