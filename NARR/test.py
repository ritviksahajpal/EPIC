import pandas, os, pdb
import json

dir = r'C:\Users\ritvik\Documents\PhD\Projects\AGMIP\json-translation-samples-master\json-translation-samples-master\Maize_Nioro'

with open(dir+os.sep+'Survey_data-Nioro-MAZ-historical.json') as json_data:
    data = json.load(json_data)

pdb.set_trace()


df = pandas.DataFrame.from_dict(data, orient='index').T.set_index('index')  

print df.head()
pdb.set_trace()