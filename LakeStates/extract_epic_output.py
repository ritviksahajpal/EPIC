import os, pdb, pandas, fnmatch

base_dir = 'C:\\Users\\ritvik\\Documents\\PhD\\Projects\\EPIC\\Cedar_Creek - Copy\\'

def parse_ANN(list_fls):
    for fl in list_fls:
        df      = pandas.read_csv(base_dir+os.sep+fl,skiprows=10,skipinitialspace=True,\
                                  usecols=['YR','DN2O'],sep=' ')
        pdb.set_trace()
        #time_df = df[(df.YR>=constants.START_YR) & (df.YR<=constants.END_YR)]
        #time_df.groupby(lambda x: xrange.year).sum()

if __name__ == '__main__':
    list_fls = fnmatch.filter(os.listdir(base_dir),'*.ANN')
    parse_ANN(list_fls)