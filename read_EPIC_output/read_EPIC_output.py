import constants, pandas, pdb
from datetime import datetime, timedelta

df = pandas.read_csv('1.DGN', skiprows = 10, delim_whitespace=True,
                     parse_dates={"datetime": [0,1,2]}, index_col="datetime",
                    date_parser=lambda x: pandas.datetime.strptime(x, '%Y %m %d'))

print df.index
print df.head()
pdb.set_trace()