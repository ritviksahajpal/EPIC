import constants, pandas, pdb, os, fnmatch, logging, pdb, numpy, datetime, re, StringIO
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
        self.db_path = constants.db_dir + os.sep + ftype + '_' + tag + '_' + self.ldir + '.db'
        self.db_name = 'sqlite:///' + self.db_path
        self.csv_path = constants.csv_dir + os.sep + ftype + '_' + tag + '_' + self.ldir + '.csv'

        # If database already exists, delete it
        try:
            os.remove(self.db_path)
            logging.info('Deleted ' + self.db_path)
        except OSError:
            pass
        self.engine  = create_engine(self.db_name)
        self.ftype   = ftype
        self.tag     = tag
        self.ifexist = 'append'

    def get_col_widths(self, fl):
        pdb.set_trace()
        df = pandas.read_table(self.epic_out_dir + os.sep + self.ftype + os.sep + fl, skiprows=constants.SKIP, header=None, nrows=1)
        wt = df.iloc[0][0]
        # Assume the columns (right-aligned) are one or more spaces followed by one or more non-space
        cols = re.findall('\s+\S+', wt)

        return [len(col) for col in cols]

    def parse_ACM(self, fls):
        list_df = []
        for idx, fl in enumerate(fls):
            df = pandas.read_csv(self.epic_out_dir + os.sep + self.ftype + os.sep + fl, skiprows=constants.SKIP,
                            skipinitialspace=True, usecols=constants.ACM_PARAMS, sep=' ')
            df['site'] = fl[:-4]
            list_df.append(df)

        frame_df = pandas.concat(list_df)
        frame_df.to_csv(self.csv_path)
        frame_df.to_sql(self.db_name, self.engine)

    def parse_ACY(self, fls):
        list_df = []
        for idx, fl in enumerate(fls):
            df = pandas.read_csv(self.epic_out_dir + os.sep + self.ftype + os.sep + fl, skiprows=constants.SKIP,
                            skipinitialspace=True, usecols=constants.ACY_PARAMS, sep=' ')
            df['site'] = fl[:-4]
            list_df.append(df)

        frame_df = pandas.concat(list_df)
        frame_df.to_csv(self.csv_path)
        frame_df.to_sql(self.db_name, self.engine)

    def parse_ANN(self, fls):
        list_df = []

        for idx, fl in enumerate(fls):
            # Get column widths
            cols_df  = pandas.read_table(self.epic_out_dir + os.sep + self.ftype + os.sep + fl, skiprows=constants.SKIP,
                                         sep=' ', skipinitialspace=True)
            widths = [5,4]
            for i in range(len(cols_df.columns.values)-2):
                widths.append(8)

            df = pandas.read_fwf(self.epic_out_dir + os.sep + self.ftype + os.sep + fl, skiprows=constants.SKIP, sep=' ',
                                 skipinitialspace=True, widths=widths)

            df['site'] = fl[:-4]
            list_df.append(df)

        frame_df = pandas.concat(list_df)
        frame_df.to_csv(self.csv_path)
        frame_df.to_sql(self.db_name, self.engine)

    def parse_ATG(self, fls):
        list_df = []
        for fl in fls:
            df = pandas.read_csv(self.epic_out_dir + os.sep + self.ftype + os.sep + fl,
                                      skiprows=constants.SKIP, skipinitialspace=True, usecols=constants.ATG_PARAMS, sep=' ')
            #time_df = df[(df.Y >= int(constants.START_YR)) & (df.Y <= int(constants.END_YR))]
            df['site'] = fl[:-4]
            list_df.append(df)

        frame_df = pandas.concat(list_df)
        frame_df.to_csv(self.csv_path)
        frame_df.to_sql(self.db_name, self.engine)

    def parse_DGN(self, fls):
        list_df = []
        for fl in fls:
            df      = pandas.read_csv(self.epic_out_dir + os.sep + self.ftype + os.sep + fl, skiprows=constants.SKIP, delim_whitespace=True,
                                      usecols=constants.DGN_PARAMS, parse_dates={"datetime": [0,1,2]}, index_col="datetime",
                                      date_parser=lambda x: pandas.datetime.strptime(x, '%Y %m %d'))
            start = df.index.searchsorted(datetime.datetime(constants.START_YR, 1, 1))
            end = df.index.searchsorted(datetime.datetime(constants.END_YR, 12, 31))
            time_df = df.ix[start:end]

            time_df = time_df.groupby(time_df.index.map(lambda x: x.year)).max()
            time_df['site'] = fl[:-4]
            list_df.append(time_df)

        frame_df = pandas.concat(list_df)
        frame_df.to_csv(self.csv_path)
        frame_df.to_sql(self.db_name, self.engine)

    def parse_SCN(self, fls):
        list_df = []
        temp_df = pandas.DataFrame()
        for fl in fls:
            df = pandas.read_csv(self.epic_out_dir + os.sep + self.ftype + os.sep + fl,
                                 skiprows=constants.SKIP_SCN, skipinitialspace=True, usecols=constants.ATG_PARAMS, sep=' ')
            df['site'] = fl[:-4]
            pdb.set_trace()
            for var in constants.SKIP_SCN:
                temp_df[var]    = df.TOT.ix[var]

        frame_df = pandas.concat(temp_df)
        frame_df.to_csv(self.csv_path)
        frame_df.to_sql(self.db_name, self.engine)

    def collect_epic_output(self, fls):
        if(self.ftype == 'DGN'):
            self.parse_DGN(fls)
        elif(self.ftype == 'ACY'):
            self.parse_ACY(fls)
        elif(self.ftype == 'ANN'):
            self.parse_ANN(fls)
        elif(self.ftype == 'ATG'):
            self.parse_ATG(fls)
        elif(self.ftype == 'SCN'):
            self.parse_SCN(fls)
        else:
            logging.info('Wrong file type')

    def sql_to_csv(self):
        epic_fl_types = constants.GET_PARAMS

        for idx, fl_name in enumerate(epic_fl_types):
            try:
                df = pandas.read_sql_table(self.db_name, self.engine)
                #df.to_csv(constants.anly_dir + os.sep + fl_name + '.csv')
            except:
                logging.info('table not found: ' + self.db_name)


if __name__ == '__main__':
    df = pandas.read_csv('C:\\Users\\ritvik\\Documents\\PhD\\Projects\\Lake_States\EPIC\\OpenLands_LS\\simulations\\LS_2013_10_18_2015_23h_42m\\0.SCN',
                         skiprows=14, skipinitialspace=True, sep=' ')
    pdb.set_trace()
    for idx, fl_name in enumerate(constants.GET_PARAMS):
        print fl_name
        obj = EPIC_Output_File(ftype=fl_name, tag=constants.TAG)
        # Get list of all output files for each EPIC output category
        list_fls = fnmatch.filter(os.listdir(obj.epic_out_dir + os.sep + constants.GET_PARAMS[idx] + os.sep), '*.' + fl_name)[:100]

        # Collec EPIC output to database and csv
        obj.collect_epic_output(list_fls)
        # Extract results
        # obj.sql_to_csv()
