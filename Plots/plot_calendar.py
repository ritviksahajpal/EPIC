import pandas, pdb, os, csv
from dbfpy import dbf

###############################################################################
#
#
#
#
###############################################################################
def dbf_to_csv(file_name):
    if file_name.endswith('.dbf'):
        #logging.info("Converting %s to csv" % file_name)
        
        csv_fn = file_name[:-4]+ ".csv"
        
        with open(csv_fn,'wb') as csvfile:
            in_db = dbf.Dbf(file_name)
            out_csv = csv.writer(csvfile)
            names = []
            for field in in_db.header.fields:
                names.append(field.name)
            out_csv.writerow(names)
            for rec in in_db:
                out_csv.writerow(rec.fieldData)
            in_db.close()
    else:
        pass
        #logging.info("\tFilename does not end with .dbf")

    return csv_fn

base_dir = 'C:/Users/ritvik/Documents/PhD/Projects/Lake_States/Code/Python/Plots/FARS2010/'
dbf_fl   = base_dir+os.sep+'accident.dbf' 
csv_fl   = dbf_to_csv(dbf_fl)

df = pandas.read_csv(csv_fl)
pdb.set_trace()
