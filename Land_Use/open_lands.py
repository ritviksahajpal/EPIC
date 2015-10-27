import constants_lu, pdb, logging, numpy, os, glob, sys, csv, multiprocessing
from multiprocessing import pool
from dbfpy import dbf

try:
    import archook
    archook.get_arcpy()
    import arcpy
    arcpy.CheckOutExtension("Spatial")
    from arcpy.sa import *
    arcpy.env.overwriteOutput = True
    arcpy.env.extent = "MAXOF"
except ImportError:
    logging.info('Missing ArcPY')

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

def create_zonal_state(state, ras, yr):
    # Perform lookup on COUNT column, since we want to perform zonal stat on area/count
    try:
        lu_tmp = Lookup(ras, 'COUNT')
        lu_ras = constants_lu.epic_dir + os.sep + state + os.sep + state + os.sep + 'LupOp_' + str(yr) + '_' + state
        lu_tmp.save(lu_ras)

        in_zone_data = constants_lu.base_dir + 'Data' + os.sep + 'GIS' + os.sep + 'UScounties' + os.sep + 'LakeStateCounty.shp'
        out_zsat     = ZonalStatisticsAsTable(in_zone_data, 'FIPS', lu_ras,
                                              constants_lu.epic_dir + os.sep + state + os.sep + 'Open_' + str(yr) + '_' + state + '_zsat.dbf',
                                              'DATA', 'SUM')
        dbf_to_csv(constants_lu.epic_dir + os.sep + state + os.sep + 'Open_' + str(yr) + '_' + state + '_zsat.dbf')
    except:
        logging.info(arcpy.GetMessages())

    logging.info('Zonal stat as table... ' + constants_lu.epic_dir + os.sep + state + os.sep + 'Open_' + str(yr) + '_' + state + '_zsat.dbf')

def filter_and_project_raster(state, ras, yr):
    odir = constants_lu.epic_dir + os.sep + state
    filtered_state = odir + os.sep + 'open_' + str(yr) + '_' + state
    tmp_ras        = odir + os.sep + 'tmp_' + str(yr) + '_' + state

    try:
        where = "COUNT > "+str(constants_lu.FILTER_SIZE)
        att_extract = ExtractByAttributes(ras,where)
        att_extract.save(tmp_ras)
    except:
        logging.info(arcpy.GetMessages())

    try:
        out_set_null = SetNull(Lookup(RegionGroup(tmp_ras,"","","NO_LINK",""),"Count") <= constants_lu.FILTER_SIZE,tmp_ras)
        out_set_null.save(filtered_state)

        # Reproject
        dsc = arcpy.Describe(ras)
        coord_sys = dsc.spatialReference
        arcpy.DefineProjection_management(filtered_state,coord_sys)
    except:
        logging.info(arcpy.GetMessages())

    logging.info('\t Filtering small pixels from state '+state)
    return filtered_state

def erase_PAD(state, ras):
    extracted_rasters = []
    # Process: Erase
    # pad_state contains input directory containing PAD files
    pad_state     = constants_lu.pad_dir + 'PAD-US_' + state + os.sep + 'PADUS1_3_' + state + '.gdb' + os.sep + 'PADUS1_3' + state
    # Output directory where we will store output
    pad_out_dir   = constants_lu.pad_dir + 'output' + os.sep + state + os.sep
    state_dir     = constants_lu.epic_dir + os.sep + state + os.sep

    constants_lu.make_dir_if_missing(pad_out_dir)
    constants_lu.make_dir_if_missing(state_dir)

    select_state  = pad_out_dir + state + '.shp'
    erased_pad    = pad_out_dir + state + '.shp'

    #
    if arcpy.Exists(select_state):
        pass
    else:
        where = '"STATE_ABBR" = ' + "'%s'" %state.upper()
        try:
            arcpy.Select_analysis(constants_lu.BOUNDARIES, select_state, where)
        except:
            logging.info(arcpy.GetMessages())

    #
    if arcpy.Exists(erased_pad):
        pass
    else:
        try:
            arcpy.Erase_analysis(select_state, pad_state, erased_pad, "")
        except:
            logging.info(arcpy.GetMessages())

    for raster in ras:
        extract_comb  = state_dir + 'ext_' + state + os.path.basename(raster)[-4:]
        try:
            arcpy.gp.ExtractByMask_sa(raster, erased_pad, extract_comb)
            extracted_rasters.append(extract_comb)
        except:
            logging.info(arcpy.GetMessages())

    logging.info('\t Erasing PAD from state ' + state)
    return extracted_rasters

def reclassify_to_open_lands(state, state_cdl_files, range_of_yrs):
    recl_rasters = []
    end_open_ras    = constants_lu.epic_dir+os.sep+state+os.sep+'IOpen_'+str(constants_lu.END_YEAR)+'_'+state # OPEN_20xx_<state_name>
    start_open_ras  = constants_lu.epic_dir+os.sep+state+os.sep+'IOpen_'+str(constants_lu.START_YEAR)+'_'+state # OPEN_20xx_<state_name>
    constants_lu.make_dir_if_missing(constants_lu.epic_dir+os.sep+state)

    # Create output directory for each state
    state_dir  = constants_lu.out_dir+os.sep+state+os.sep
    constants_lu.make_dir_if_missing(state_dir)

    # Reclass for each year
    for idx, yr in enumerate(range_of_yrs):
        recl_raster = constants_lu.epic_dir + os.sep + state + os.sep + constants_lu.RECL + '_' + state + '_' + str(yr)

        try:
            out_reclass = arcpy.sa.ReclassByASCIIFile(state_cdl_files[idx], constants_lu.REMAP_FILE, 'NODATA')
            out_reclass.save(recl_raster)
            recl_rasters.append(recl_raster)
        except:
            logging.info(arcpy.GetMessages())

        logging.info('\tReclassified...' + recl_raster)

        # Extract open land acreage in the last year
        if (yr == constants_lu.END_YEAR):
            where = "VALUE = "+str(constants_lu.OPEN)
            try:
                att_extract = ExtractByAttributes(recl_raster,where)
                att_extract.save(end_open_ras)

                create_zonal_state(state, end_open_ras, constants_lu.START_YEAR)
            except:
                logging.info(arcpy.GetMessages())
                logging.info('\tExtracted Open Lands...'+end_open_ras)
        elif(yr == constants_lu.START_YEAR): # Extract open land acreage in the first year:
            where = "VALUE = "+str(constants_lu.OPEN)
            try:
                att_extract = ExtractByAttributes(recl_raster,where)
                att_extract.save(start_open_ras)

                create_zonal_state(state, start_open_ras, constants_lu.END_YEAR)
            except:
                logging.info(arcpy.GetMessages())
                logging.info('\tExtracted Open Lands...'+start_open_ras)

    return recl_rasters

def open_lands_conv(state):
    # Loop across all states
    state_cdl_files = []
    range_of_yrs    = numpy.array((constants_lu.START_YEAR, constants_lu.END_YEAR))

    for subdir, dir_list, files in os.walk(constants_lu.cdl_dir):
        break

    # Collect all CDL files for state within given year range
    for yr in range_of_yrs:
        for position, item in enumerate(dir_list):
            if (str(yr) in item): # e.g. 2008 is in 2008_cdls
                cdl_file = glob.glob(constants_lu.cdl_dir+os.sep+dir_list[position]+os.sep+state+os.sep+'*_'+state+'_*'+str(yr)+'*.tif')
                if cdl_file:
                    state_cdl_files.append(''.join(cdl_file))
                else:
                    logging.info(cdl_file + 'not found!')
                    sys.exit(0)

    # Set snap extent
    arcpy.env.snapRaster = state_cdl_files[0]
    logging.info('\tSet snap extent')

    # 1. Reclassify CDL (START_YEAR , END_YEAR)
    open_rasters = reclassify_to_open_lands(state, state_cdl_files, range_of_yrs)

    # 2. Erase the PAD
    extract_ras  = erase_PAD(state, open_rasters)

    # 3. Filter the raster
    for ras in extract_ras:
        yr = os.path.basename(ras)[-4:]
        filter_and_project_raster(state, ras, yr)

if __name__ == "__main__":
    logging.info('start')
    pool = multiprocessing.Pool(constants_lu.max_threads)
    list_files = pool.map(open_lands_conv, constants_lu.list_st)
    pool.close()
    pool.join()

    logging.info('Done!')