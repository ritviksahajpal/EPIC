import constants, pandas, pdb, os, fnmatch, logging, pdb, csv
from dbfpy import dbf
try:
    import archook
    archook.get_arcpy()
    import arcpy
    from arcpy.sa import *
except ImportError:
    logging.info('Missing ArcPY')

# ArcGIS constants
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput = True
arcpy.env.extent = "MAXOF"

def dbf_to_csv(file_name):
    if file_name.endswith('.dbf'):
        logging.info("Converting %s to csv" % file_name)

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
        logging.info("\tFilename does not end with .dbf")

    return csv_fn

def tabulate_area_ras(raster='', tab_field='', zone_data='', zone_fld='', out_fname=''):
    out_dbf  = constants.gis_dir + os.sep + raster + '.dbf'
    merg_ras = constants.gis_dir + os.sep + 'lup_' + raster

    if arcpy.Exists(out_dbf[:-4]+'.csv'):
        pass
    else:
        try:
            # Execute Lookup
            out_ras = Lookup(raster, tab_field)

            # Save the output
            out_ras.save(merg_ras)

            # Zonal stat
            ZonalStatisticsAsTable(zone_data, zone_fld, merg_ras, out_dbf, "DATA", "SUM")
            dbf_to_csv(out_dbf)
        except:
            logging.info(arcpy.GetMessages())

    logging.info('\t Tabulating area for ...' + raster)
    return out_dbf[:-4] + '.csv'

if __name__ == '__main__':
    pass
