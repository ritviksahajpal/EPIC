##################################################################
# merge_ssurgo.py Apr 2015
# ritvik sahajpal (ritvik@umd.edu)
# 
##################################################################
import multiprocessing, constants, logging, arcpy, fnmatch, os, csv
from arcpy.sa import *

def delete_temp_files(files_to_delete):
    for fl in files_to_delete:
        logging.info('Deleting: '+fl)
        try:
            arcpy.Delete_management(fl,"")
        except:
            logging.info(arcpy.GetMessages())

def merge_ssurgo_rasters(st):
    files_to_delete = [] # Temporary files which will be deleted at the end
        
    # We use the spatial reference information from the CDL to reproject (if needed) the other data layers
    cdl_file = constants.cdl_dir+os.sep+constants.CDL_STATE+os.sep+\
                fnmatch.filter(os.listdir(constants.cdl_dir+os.sep+constants.CDL_STATE),'*.tif')[0]
    cdl_spatial_ref = arcpy.CreateSpatialReference_management(cdl_file, "", "", "", "", "", "0")

    # Iterate over all the states contained in the dictionary state_names
    logging.info(st[1])
        
    # Output directory to store merged SSURGO files for each state
    out_ssurgo_dir = constants.r_soil_dir+os.sep+constants.SOIL+os.sep+st[1] 
    constants.make_dir_if_missing(out_ssurgo_dir+os.sep+constants.CATALOG)

    # For each state, process the SSURGO spatial files
    for dir_name, subdir_list, file_list in os.walk(constants.data_dir):
        if('_'+st[1]+'_' in dir_name and constants.SPATIAL in subdir_list):
            in_ssurgo_dir = dir_name+os.sep+constants.SPATIAL+os.sep

            # The reclassification is done to make the VALUE equal to the MUKEY
            recl_ssurgo_csv = open(out_ssurgo_dir+os.sep+st[1]+'.csv', 'wb')
            recl_ssurgo_csv.write('FROM, TO, VALUE\n')
            recl_ssurgo_csv.flush()   

            # Iterate through each of the soil files for a given state
            in_ssurgo_file = dir_name+os.sep+constants.SPATIAL+os.sep+\
                            fnmatch.filter(os.listdir(dir_name+os.sep+constants.SPATIAL+os.sep),\
                            'soilmu_a_*.shp')[0]

            # reproj_file is the name of the reprojected ssurgo file
            reproj_file      = out_ssurgo_dir+os.sep+os.path.basename(in_ssurgo_file[:-4])+'_reproj.shp'

            # out_ssurgo_file is the reprojected and reclassified (to CDL resolution) SSURGO file
            out_ssurgo_file  = out_ssurgo_dir+os.sep+os.path.basename(in_ssurgo_file[:-4])[9:]

            # reclass_ssurgo_file has the MUKEY as the VALUE column
            recl_ssurgo_file = out_ssurgo_dir+os.sep+constants.CATALOG+os.sep+\
                               os.path.basename(in_ssurgo_file[:-4])[9:]+'_recl'

            # Append the files to the list of ssurgo files to be merged to form one raster 
            merged_soil_folder = out_ssurgo_dir
            merged_soil_file   = st[1]+'_'+constants.SOIL
            if(not(os.path.isfile(recl_ssurgo_file))):
                logging.info('Shapefile '+os.path.basename(in_ssurgo_file)+\
                            ' is being reprojected, reclassified and converted to raster '+\
                            os.path.basename(out_ssurgo_file))
        
                try:
                    arcpy.Project_management(in_ssurgo_file, reproj_file, cdl_spatial_ref)
                    arcpy.FeatureToRaster_conversion(reproj_file, constants.MUKEY, out_ssurgo_file, constants.cdl_res)

                    recl_ssurgo_csv = open(out_ssurgo_dir+os.sep+st[1]+'.csv', 'a+')
                    cur = arcpy.SearchCursor(out_ssurgo_file)
                    row=cur.next()

                    while row:
                        recl_ssurgo_csv.write(str(row.getValue("VALUE"))+', '+str(row.getValue("VALUE"))+', '+row.getValue(constants.MUKEY)+'\n')
                        row = cur.next()
                    recl_ssurgo_csv.close()

                    out_reclass = ReclassByTable(out_ssurgo_file,out_ssurgo_dir+os.sep+st[1]+'.csv', "FROM", "TO", "VALUE", "DATA")
                    out_reclass.save(recl_ssurgo_file)

                    files_to_delete.append(out_ssurgo_file)
                    files_to_delete.append(recl_ssurgo_file)
                    files_to_delete.append(reproj_file)
                except:
                    logging.info(arcpy.GetMessages())
                    delete_temp_files(files_to_delete)
            else:
                logging.info('File present: '+recl_ssurgo_file)

    if(not(os.path.isfile(merged_soil_folder+os.sep+merged_soil_file))):
        # Create a raster catalog
        logging.info('Creating and populating a raster catalog with SSURGO files')
        try:
            arcpy.CreateFileGDB_management(out_ssurgo_dir, st[1]+constants.SOIL+'.gdb')
            arcpy.CreateRasterCatalog_management(out_ssurgo_dir+os.sep+st[1]+constants.SOIL+'.gdb',\
                                                    st[1],"", "", "", "", "", "","", "")
            arcpy.WorkspaceToRasterCatalog_management(out_ssurgo_dir+os.sep+constants.CATALOG,out_ssurgo_dir+\
                                                        os.sep+st[1]+constants.SOIL+'.gdb'+os.sep+st[1],"","")
        except:
            logging.info(arcpy.GetMessages())
            delete_temp_files(files_to_delete)

        # Merge all reprojected and reclassified rasters into one
        try:
            logging.info('Merging...')
            arcpy.RasterCatalogToRasterDataset_management(out_ssurgo_dir+os.sep+st[1]+constants.SOIL+'.gdb'+os.sep+st[1],
                                                    merged_soil_folder+os.sep+merged_soil_file,
                                                    "", "LAST", "FIRST", "", "", "", "", "", "", "")        
        except:
            logging.info(arcpy.GetMessages())
            delete_temp_files(files_to_delete)
            
        delete_temp_files(files_to_delete)
        logging.info('Finished processing '+st[0])
    else:
        logging.info('File present: '+merged_soil_folder+os.sep+merged_soil_file)

def run_merge_ssurgo_rasters(): 
    # Read file containing list of states to process
    fname = constants.base_dir+os.sep+constants.INPUT+os.sep+constants.LIST_STATES
    
    with open(fname, 'rb') as f:
        reader  = csv.reader(f)
        list_st = list(reader)

    pool = multiprocessing.Pool(constants.max_threads)
    pool.map(merge_ssurgo_rasters,list_st)
    pool.close()
    pool.join()    

if __name__ == "__main__":
    run_merge_ssurgo_rasters()
