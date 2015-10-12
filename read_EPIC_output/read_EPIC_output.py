import constants, pandas, pdb, os, fnmatch, logging, pdb, numpy, datetime, sqlite3
from sqlalchemy import create_engine

class EPIC_Output_File():
    """
    Class to read EPIC Output files
    """
    def __init__(self, ftype='', tag=''):
        """
        Constructor
        """
        # Get name of latest output directory (based on what time it was modified)
        os.chdir(constants.epic_dir+os.sep+'output')
        dirs = [d for d in os.listdir(constants.epic_dir+os.sep+'output') if os.path.isdir(constants.epic_dir+os.sep+'output')]
        self.ldir = sorted(dirs, key=lambda x: os.path.getmtime(x), reverse=True)[:1][0]
        self.epic_out_dir = constants.epic_dir + os.sep + 'output' + os.sep + self.ldir # Latest output directory

        # Create a sqlite database in the analysis directory
        self.db_name = 'sqlite:///' + constants.anly_dir + '/' + ftype + '_' + tag + '_' + self.ldir + '.db'
        # If database already exists, delete it
        try:
            os.remove(self.db_name)
        except OSError:
            pass
        self.engine  = create_engine(self.db_name)
        self.ftype   = ftype
        self.tag     = tag
        self.ifexist = 'append'

    def parse_ACY(self, fls):
        for fl in fls:
            df = pandas.read_csv(self.epic_out_dir + os.sep + self.ftype + os.sep + fl, skiprows=constants.SKIP,
                            skipinitialspace=True, usecols=constants.ACY_PARAMS, sep=' ')
            time_df = df[(df.YR >= constants.START_YR) & (df.YR <= constants.END_YR)]
            time_df['site'] = fl[:-4]
            time_df.to_sql(self.db_name, self.engine, if_exists=self.ifexist)

    def parse_ANN(self, fls):
        for fl in fls:
            # Get column widths
            cols_df  = pandas.read_table(self.epic_out_dir + os.sep + self.ftype + os.sep + fl, skiprows=constants.SKIP,
                                         sep=' ', skipinitialspace=True)
            widths = [5,4]
            for i in range(len(cols_df.columns.values)-2):
                widths.append(8)

            df = pandas.read_fwf(self.epic_out_dir + os.sep + self.ftype + os.sep + fl, skiprows=constants.SKIP, sep=' ',
                                 skipinitialspace=True, widths=widths)

            time_df = df[(df.YR >= constants.START_YR) & (df.YR <= constants.END_YR)]
            time_df['site'] = fl[:-4]
            time_df.to_sql(self.db_name, self.engine, if_exists=self.ifexist)

    def parse_DGN(self, fls):
        for fl in fls:
            df      = pandas.read_csv(self.epic_out_dir + os.sep + self.ftype + os.sep + fl, skiprows=constants.SKIP, delim_whitespace=True,
                                      usecols=constants.DGN_PARAMS, parse_dates={"datetime": [0,1,2]}, index_col="datetime",
                                      date_parser=lambda x: pandas.datetime.strptime(x, '%Y %m %d'))
            start = df.index.searchsorted(datetime.datetime(constants.START_YR, 1, 1))
            end = df.index.searchsorted(datetime.datetime(constants.END_YR, 12, 31))
            time_df = df.ix[start:end]

            time_df = time_df.groupby(time_df.index.map(lambda x: x.year)).max()
            time_df['site'] = fl[:-4]
            time_df.to_sql(self.db_name, self.engine, if_exists=self.ifexist)

    def parse_ATG(self, fls):
        for fl in fls:
            print fl
            df      = pandas.read_csv(self.epic_out_dir + os.sep + self.ftype + os.sep + fl,
                                      skiprows=constants.SKIP, skipinitialspace=True, usecols=constants.ATG_PARAMS, sep=' ')
            time_df = df[(df.Y >= int(constants.START_YR)) & (df.Y <= int(constants.END_YR))]
            time_df['site'] = fl[:-4]
            time_df.to_sql(self.db_name, self.engine, if_exists=self.ifexist)

    def collect_epic_output(self, fls):
        if(self.ftype == 'DGN'):
            self.parse_DGN(fls)
        elif(self.ftype == 'ACY'):
            self.parse_ACY(fls)
        elif(self.ftype == 'ANN'):
            self.parse_ANN(fls)
        elif(self.ftype == 'ATG'):
            self.parse_ATG(fls)
        else:
            logging.info( 'Wrong file type')

    def sql_to_csv(self):
        epic_fl_types = constants.GET_PARAMS

        for idx, fl_name in enumerate(epic_fl_types):
            try:
                df = pandas.read_sql_table(self.db_name, self.engine)
                #df.to_csv()
            except:
                logging.info('table not found: ' + self.db_name)


if __name__ == '__main__':
    epic_fl_types = constants.GET_PARAMS

    for idx, fl_name in enumerate(epic_fl_types):
        obj = EPIC_Output_File(ftype=fl_name, tag=constants.TAG)
        list_fls = fnmatch.filter(os.listdir(obj.epic_out_dir + os.sep + constants.GET_PARAMS[idx] + os.sep), '*.' + fl_name)
        obj.collect_epic_output(list_fls)
        obj.sql_to_csv()
