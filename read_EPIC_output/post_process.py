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
    """
    :param raster:
    :param tab_field:
    :param zone_data:
    :param zone_fld:
    :param out_fname:
    :return:
    """
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

            out_zonal_statistics = ZonalStatistics(in_zone_data, 'FIPS', constants.out_dir+'lup_'+state+'_'+constants.METRIC,"SUM","DATA")
            out_zonal_statistics.save(constants.out_dir+state+'_zsat')
            logging.info('Zonal stat... '+constants.out_dir+state+'_zsat')

        except:
            logging.info('\t Tabulating area for ...' + raster)
    return out_dbf[:-4] + '.csv'

def process_IPCC_carbon_2000(zone_data='', zone_fld=''):
    try:
        out_int_ras = constants.gis_dir + os.sep + 'int_IPCC_c'
        out_zon_ras = constants.gis_dir + os.sep + 'zon_IPCC_c'
        out_zon_dbf = constants.csv_dir + os.sep + 'zon_IPCC_c.dbf'

        # Convert IPCC carbon file to one with integer values in VALUE column
        if not arcpy.Exists(out_int_ras):
            out_int = Int(constants.IPCC_FILE)
            out_int.save(out_int_ras)
            logging.info('Converted to int ' + out_int_ras)

        # Perform zonal statistics on integer raster
        if not arcpy.Exists(out_zon_ras):
            out_zonal = ZonalStatistics(zone_data, zone_fld, out_int_ras, "MEAN", "DATA")
            out_zonal.save(out_zon_ras)
            logging.info('Zonal stats ' + out_zon_ras)

        # Zonal stat as table
        if not arcpy.Exists(out_zon_dbf):
            ZonalStatisticsAsTable(zone_data, zone_fld, out_int_ras, out_zon_dbf, "DATA", "MEAN")
            dbf_to_csv(out_zon_dbf)
            logging.info('Zonal stats as table' + out_zon_dbf)
    except:
        logging.info(arcpy.GetMessages())

if __name__ == '__main__':
    tabulate_area_ras(raster='', tab_field='', zone_data='', zone_fld='', out_fname='')
    #process_IPCC_carbon_2000(zone_data=constants.zone_data, zone_fld='FIPS')
