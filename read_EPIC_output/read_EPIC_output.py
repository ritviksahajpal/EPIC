import constants, pandas, pdb, os, fnmatch, logging, pdb, numpy, datetime
from sqlalchemy import create_engine
from multiprocessing.dummy import Pool

class EPIC_Output_File():
    """
    Class to read EPIC Output files
    """
    def __init__(self, ftype='', tag=''):
        """
        Constructor
        """
        # Create a sqlite database in the analysis directory
        self.db_name = 'sqlite:///' + constants.anly_dir + os.sep + ftype + '_' + tag + '.db'
        self.engine  = create_engine(self.db_name)
        self.ftype   = ftype
        self.tag     = tag

        # Get name of latest output directory (based on what time it was modified)
        os.chdir(constants.epic_dir+os.sep+'output')
        dirs = [d for d in os.listdir(constants.epic_dir+os.sep+'output') if os.path.isdir(constants.epic_dir+os.sep+'output')]
        self.epic_out_dir = constants.epic_dir + os.sep + 'output' + os.sep + \
                            sorted(dirs, key=lambda x: os.path.getmtime(x), reverse=True)[:1][0] # Latest output directory

    def parse_ACY(self, fl):
        pdb.set_trace()
        df      = pandas.read_csv(self.epic_out_dir + os.sep + self.ftype + os.sep + fl, skiprows=constants.SKIP,
                                  skipinitialspace=True, usecols=constants.ACY_PARAMS, sep=' ')
        time_df = df[(df.YR >= constants.START_YR) & (df.YR <= constants.END_YR)]
        time_df['site'] = fl[:-4]
        time_df.to_sql(self.db_name, self.engine, if_exists='append')

    def parse_ANN(self, fl):
        df = pandas.read_csv(self.epic_out_dir + os.sep + self.ftype + os.sep + fl, skiprows=constants.SKIP, skipinitialspace=True,
                             usecols=constants.ANN_PARAMS, sep=' ')
        pdb.set_trace()
        time_df = df[(df.YR >= constants.START_YR) & (df.YR <= constants.END_YR)]
        time_df['site'] = fl[:-4]
        time_df.to_sql(self.db_name, self.engine, if_exists='append')

    def parse_DGN(self, fl):
        df      = pandas.read_csv(self.epic_out_dir + os.sep + self.ftype + os.sep + fl, skiprows=constants.SKIP, delim_whitespace=True,
                                  usecols=constants.DGN_PARAMS, parse_dates={"datetime": [0,1,2]}, index_col="datetime",
                                  date_parser=lambda x: pandas.datetime.strptime(x, '%Y %m %d'))
        start = df.index.searchsorted(datetime.datetime(constants.START_YR, 1, 1))
        end = df.index.searchsorted(datetime.datetime(constants.END_YR, 12, 31))
        time_df = df.ix[start:end]

        time_df = time_df.groupby(time_df.index.map(lambda x: x.year)).max()
        time_df['site'] = fl[:-4]
        time_df.to_sql(self.db_name, self.engine, if_exists='append')

    def parse_ATG(self, fl):
        df      = pandas.read_csv(self.epic_out_dir + os.sep + self.ftype + os.sep + constants.GET_PARAMS[0] + os.sep + fl,
                                  skiprows=constants.SKIP, skipinitialspace=True, usecols=constants.ATG_PARAMS, sep=' ')
        time_df = df[(df.Y >= int(constants.START_YR)) & (df.Y <= int(constants.END_YR))]
        time_df['site'] = fl[:-4]

        return fl[:-4], time_df.BIOM.max() - time_df.RWT.max()
        #pdb.set_trace()
        #time_df.to_sql(self.db_name, self.engine, if_exists='append')

    def collect_epic_output(self, fls):
        pool = Pool(constants.max_threads)
        if(self.ftype == 'DGN'):
            self.parse_DGN(fls[0])
            pass #pool.map(self.parse_DGN, fls)
        elif(self.ftype == 'ACY'):
            #pool.map(self.parse_ACY, fls)
            self.parse_ACY(fls[0])
        elif(self.ftype == 'ANN'):
            #pool.map(self.parse_ANN, fls)
            pass #self.parse_ANN(fls[0])
        elif(self.ftype == 'ATG'):
            pass #self.parse_ATG(fls[0])
            #pool.map(self.parse_ATG, fls)
        else:
            logging.info( 'Wrong file type')

    def sql_to_csv(self):
        fls = ''
        dfs = pandas.DataFrame(index=numpy.arange(0, len(fls)), columns=['site','biom_rwt'])

        for idx, f in enumerate(fls):
            st, val = self.parse_ATG(f)
            dfs.loc[idx] = [st, val]
        dfs.to_csv('C:\\Users\\ritvik\\Documents\PhD\\Projects\\Lake_States\\EPIC\\OpenLands_LS\\out_wi.csv')

if __name__ == '__main__':
    epic_fl_types = constants.GET_PARAMS

    for idx, fl_name in enumerate(epic_fl_types):
        obj = EPIC_Output_File(ftype=fl_name, tag=constants.TAG)
        list_fls = fnmatch.filter(os.listdir(obj.epic_out_dir + os.sep + constants.GET_PARAMS[idx] + os.sep), '*.' + fl_name)
        obj.collect_epic_output(list_fls)
