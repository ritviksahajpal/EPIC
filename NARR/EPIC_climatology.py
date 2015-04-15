import pandas as pd

dates = pd.date_range('1950-01-01', '1953-12-31', freq='D')
data  = [int(1000*random.random()) for i in xrange(len(dates))]
cum_data = pd.Series(data, index=dates)
#grouped = cum_data.groupby(lambda x: x.year)
#grouped.fillna(method='pad')
cum_data.groupby(cum_data.index.dayofyear).mean()
cum_data.to_csv('C:\\test.csv', sep="\t")

for i in df.index:
    do_something(df.ix[i])