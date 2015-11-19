import constants, pandas, pdb, os, fnmatch, logging, pdb, numpy, datetime, re, StringIO
from sqlalchemy import create_engine

dd = 'C:\\Users\\ritvik\\Documents\\PhD\\Projects\\Lake_States\\EPIC\\OpenLands_LS\\simulations\\LS_2013_11_19_2015_10h_35m\\1.ACN'
# read in file
fl = pandas.read_csv(dd, skiprows=12)
import pdb
pdb.set_trace()

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

        # Get list of all directories in output folder, select the ones which have the current TAG
        dirs = [d for d in os.listdir(constants.epic_dir+os.sep+'output') if os.path.isdir(constants.epic_dir+os.sep+'output')]
        cur_dirs = [d for d in dirs if constants.OUT_TAG in d]

        # Select the TAGged directory which is the latest
        self.ldir = sorted(cur_dirs, key=lambda x: os.path.getmtime(x), reverse=True)[:1][0]
        if constants.DO_FOLDER:
            self.epic_out_dir = constants.FOLDER_PATH
        else:
            self.epic_out_dir = constants.epic_dir + os.sep + 'output' + os.sep + self.ldir # Latest output directory

        # Create a sqlite database in the analysis directory
        self.db_path = constants.db_dir + os.sep + ftype + '_' + tag + '_' + self.ldir + '.db'
        self.db_name = 'sqlite:///' + self.db_path
        self.csv_path = constants.csv_dir + os.sep + ftype + '_' + tag + '_' + self.ldir + '.csv'

        self.engine  = create_engine(self.db_name)
        self.ftype   = ftype
        self.tag     = tag
        self.ifexist = 'replace'

    def get_col_widths(self, fl):
        df = pandas.read_table(self.epic_out_dir + os.sep + self.ftype + os.sep + fl, skiprows=constants.SKIP, header=None, nrows=1)
        wt = df.iloc[0][0]
        # Assume the columns (right-aligned) are one or more spaces followed by one or more non-space
        cols = re.findall('\s+\S+', wt)

        return [len(col) for col in cols]

    ###############################
    # ACM
    ###############################
    def parse_ACM(self, fls):
        list_df = []
        for idx, fl in enumerate(fls):
            try:
                df = pandas.read_csv(self.epic_out_dir + os.sep + self.ftype + os.sep + fl, skiprows=constants.SKIP,
                            skipinitialspace=True, usecols=constants.ACM_PARAMS, sep=' ')
            except:
                logging.info('Error reading ' + fl)
            df['site'] = fl[:-4]
            list_df.append(df)

        frame_df = pandas.concat(list_df)
        frame_df.to_csv(self.csv_path)
        frame_df.to_sql(self.db_name, self.engine, if_exists=self.ifexist)

    ###############################
    # ACY
    ###############################
    def parse_ACY(self, fls):
        list_df = []
        for idx, fl in enumerate(fls):
            try:
                df = pandas.read_csv(self.epic_out_dir + os.sep + self.ftype + os.sep + fl, skiprows=constants.SKIP,
                            skipinitialspace=True, usecols=constants.ACY_PARAMS, sep=' ')
            except:
                logging.info('Error reading ' + fl)
            df['site'] = fl[:-4]
            list_df.append(df)

        frame_df = pandas.concat(list_df)
        frame_df.to_csv(self.csv_path)
        frame_df.to_sql(self.db_name, self.engine, if_exists=self.ifexist)

    ###############################
    # ANN
    ###############################
    def parse_ANN(self, fls):
        list_df = []
        # Get column widths
        cols_df  = pandas.read_table(self.epic_out_dir + os.sep + self.ftype + os.sep + fls[0], skiprows=constants.SKIP,
                                     sep=' ', skipinitialspace=True)
        widths = [5,4]
        for i in range(len(cols_df.columns.values)-2):
            widths.append(8)

        for idx, fl in enumerate(fls):
            try:
                df = pandas.read_fwf(self.epic_out_dir + os.sep + self.ftype + os.sep + fl, skiprows=constants.SKIP, sep=' ',
                                 usecols=constants.ANN_PARAMS, skipinitialspace=True, widths=widths)
            except:
                logging.info('Error reading ' + fl)

            df['site'] = fl[:-4]
            list_df.append(df)

        frame_df = pandas.concat(list_df)
        frame_df.to_csv(self.csv_path)
        frame_df.to_sql(self.db_name, self.engine, if_exists=self.ifexist)

    ###############################
    # ATG
    ###############################
    def parse_ATG(self, fls):
        list_df = []
        for fl in fls:
            try:
                df = pandas.read_csv(self.epic_out_dir + os.sep + self.ftype + os.sep + fl,
                                      skiprows=constants.SKIP, skipinitialspace=True, usecols=constants.ATG_PARAMS, sep=' ')
            except:
                logging.info('Error reading ' + fl)
            #time_df = df[(df.Y >= int(constants.START_YR)) & (df.Y <= int(constants.END_YR))]
            df['site'] = fl[:-4]
            df.rename(columns={'Y': 'YR'}, inplace=True)
            list_df.append(df)

        frame_df = pandas.concat(list_df)
        frame_df.to_csv(self.csv_path)
        frame_df.to_sql(self.db_name, self.engine, if_exists=self.ifexist)

    ###############################
    # DGN
    ###############################
    def parse_DGN(self, fls):
        list_df = []
        for fl in fls:
            try:
                df      = pandas.read_csv(self.epic_out_dir + os.sep + self.ftype + os.sep + fl, skiprows=constants.SKIP, delim_whitespace=True,
                                      usecols=constants.DGN_PARAMS, parse_dates={"datetime": [0,1,2]}, index_col="datetime",
                                      date_parser=lambda x: pandas.datetime.strptime(x, '%Y %m %d'))
            except:
                logging.info('Error reading ' + fl)
            start = df.index.searchsorted(datetime.datetime(constants.START_YR, 1, 1))
            end = df.index.searchsorted(datetime.datetime(constants.END_YR, 12, 31))
            time_df = df.ix[start:end]

            time_df = time_df.groupby(time_df.index.map(lambda x: x.year)).max()
            time_df['site'] = fl[:-4]
            list_df.append(time_df)

        frame_df = pandas.concat(list_df)
        frame_df.to_csv(self.csv_path)
        frame_df.to_sql(self.db_name, self.engine, if_exists=self.ifexist)

    ###############################
    # SCN
    ###############################
    def parse_SCN(self, fls):
        list_df = []
        for idx, fl in enumerate(fls):
            temp_df = pandas.DataFrame(index=[constants.END_YR], columns=constants.SCN_PARAMS)
            try:
                df = pandas.read_csv(self.epic_out_dir + os.sep + self.ftype + os.sep + fl,
                                 skiprows=constants.SKIP_SCN, skipinitialspace=True, sep=' ')
            except:
                logging.info('Error reading ' + fl)

            for var in constants.SCN_PARAMS:
                temp_df[var]    = df.TOT.ix[var]
            temp_df['site'] = fl[:-4]
            temp_df['YR'] = temp_df.index
            list_df.append(temp_df)

        frame_df = pandas.concat(list_df)
        frame_df.index = range(len(frame_df))
        frame_df.to_csv(self.csv_path)
        frame_df.to_sql(self.db_name, self.engine, if_exists=self.ifexist)

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
        elif(self.ftype == 'ACM'):
            self.parse_ACM(fls)
        else:
            logging.info('Wrong file type')

def sql_to_csv():
    """
    SQL stores information from all years. We then extract information for the latest year from this file
    :return:
    """
    epic_fl_types = constants.GET_PARAMS
    dfs = pandas.DataFrame()

    for idx, fl_name in enumerate(epic_fl_types):
        obj = EPIC_Output_File(ftype=fl_name, tag=constants.TAG)
        try:
            df = pandas.read_sql_table(obj.db_name, obj.engine)
        except:
            logging.info(obj.db_name + ' not found')
        if fl_name <> 'SCN':
            max_yr = df.YR.unique().max()
            fyr_df = df[df.YR == max_yr] # final year df, maybe use constants.END_YR instead of max_yr?
            if idx == 0:
                dfs = fyr_df
            else:
                dfs = pandas.merge(dfs, fyr_df, on=['YR','site'], how='outer')
        else:
            if idx == 0:
                dfs = df
            else:
                dfs = pandas.merge(dfs, df, on=['YR','site'], how='outer')

    # Merge with EPICRUN.DAT
    epic_df = pandas.read_csv(constants.sims_dir + os.sep + obj.ldir + os.sep + 'EPICRUN.DAT', sep='\s+', header=None)
    epic_df.columns = ['ASTN', 'ISIT', 'IWP1','IWP5', 'IWND', 'INPS', 'IOPS', 'IWTH']

    # 1. Read ieSllist.dat and get mukey and corresponding index
    # 2. Convert to dataframe
    # 3. Merge with SSURGO properties csv file
    # 4. Merge EPIC outputs with EPICRUN.DAT
    # 5. Merge EPIC and SSURGO and output to csv
    soil_dict = {}
    with open(constants.sims_dir + os.sep + obj.ldir + os.sep + constants.SLLIST) as f:
        for line in f:
            #Sample line from soil file:     1     "Soils//1003958.sol"
            (key, val)     = int(line.split()[0]), int(line.split('//')[1].split('.')[0])
            soil_dict[key] = val

    soil_df = pandas.DataFrame.from_dict(soil_dict, orient='index').reset_index()
    soil_df.columns = ['INPS', 'mukey']

    sgo_file = pandas.read_csv(constants.sgo_dir + os.sep + constants.dominant)
    grp_sgo  = sgo_file.groupby('mukey').mean().reset_index()
    grp_sgo  = pandas.merge(grp_sgo, soil_df, on='mukey')

    # Merge with EPICRUN
    dfs[['site']] = dfs[['site']].astype(int)
    epic_df[['ASTN']] = epic_df[['ASTN']].astype(int) # ASTN is site number
    dfs = pandas.merge(dfs, epic_df, left_on='site', right_on='ASTN')

    # Merge with SSURGO file
    dfs = pandas.merge(dfs, grp_sgo, on='INPS') # INPS is identifier of soil files

    dfs.to_csv(constants.csv_dir + os.sep + 'EPIC_' + obj.ldir + '.csv')

if __name__ == '__main__':
    for idx, fl_name in enumerate(constants.GET_PARAMS):
        print idx, fl_name
        obj = EPIC_Output_File(ftype=fl_name, tag=constants.TAG)
        # Get list of all output files for each EPIC output category
        try:
            list_fls = fnmatch.filter(os.listdir(obj.epic_out_dir + os.sep + constants.GET_PARAMS[idx] + os.sep), '*.' + fl_name)

            # Collect EPIC output to database and csv
            if len(list_fls) > 0:
                obj.collect_epic_output(list_fls)
        except:
            logging.info('Error in reading ' + fl_name)

    # Extract results
    sql_to_csv()
