##################################################################
# merge_ssurgo.py Apr 2015
# ritvik sahajpal (ritvik@umd.edu)
# 
##################################################################
import multiprocessing, constants, logging, arcpy, fnmatch, os, csv
from arcpy.sa import *

# ArcGIS initialization
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput = True
arcpy.env.extent = "MAXOF"

def delete_temp_files(files_to_delete):
    for fl in files_to_delete:
        logging.info('Deleting: '+fl)
        try:
            arcpy.Delete_management(fl,"")
        except:
            logging.info(arcpy.GetMessages())

def merge_ssurgo_rasters(st):
    files_to_delete = [] # Temporary files which will be deleted at the end
    list_sgo_files  = [] # List of SSURGO files to merge
    
    cdl_spatial_ref = arcpy.SpatialReference('NAD 1983 Contiguous USA Albers')
    
    # Iterate over all the states contained in the dictionary state_names
    logging.info(st)
        
    # Output directory to store merged SSURGO files for each state
    out_ssurgo_dir = constants.r_soil_dir+os.sep+constants.SOIL+os.sep+st 
    constants.make_dir_if_missing(out_ssurgo_dir)

    # For each state, process the SSURGO spatial files
    for dir_name, subdir_list, file_list in os.walk(constants.data_dir):
        if '_'+st+'_' in dir_name and constants.SPATIAL in subdir_list:
            in_ssurgo_dir = dir_name+os.sep+constants.SPATIAL+os.sep

            # The reclassification is done to make the VALUE equal to the MUKEY
            recl_ssurgo_csv = open(out_ssurgo_dir+os.sep+st+'.csv', 'wb')
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
            recl_ssurgo_file = out_ssurgo_dir+os.sep+os.path.basename(in_ssurgo_file[:-4])[9:]+'_recl'
            list_sgo_files.append(recl_ssurgo_file)

            # Append the files to the list of ssurgo files to be merged to form one raster 
            merged_soil_folder = out_ssurgo_dir
            merged_soil_file   = st+'_'+constants.SOIL
            
            files_to_delete.append(out_ssurgo_file)
            files_to_delete.append(recl_ssurgo_file)
            files_to_delete.append(reproj_file)
            
            if not(arcpy.Exists(recl_ssurgo_file)):
                logging.info('Shapefile '+os.path.basename(in_ssurgo_file)+\
                            ' is being reprojected, reclassified and converted to raster '+\
                            os.path.basename(out_ssurgo_file))
        
                try:
                    arcpy.Project_management(in_ssurgo_file, reproj_file, cdl_spatial_ref)
                    arcpy.FeatureToRaster_conversion(reproj_file, constants.MUKEY, out_ssurgo_file, constants.cdl_res)

                    # Create table for performing reclassification
                    recl_ssurgo_csv = open(out_ssurgo_dir+os.sep+st+'.csv', 'a+')
                    with arcpy.da.SearchCursor(out_ssurgo_file, ['VALUE',constants.MUKEY]) as cursor:
                        for row in cursor:
                            recl_ssurgo_csv.write(str(row[0])+', '+str(row[0])+', '+str(row[1])+'\n')        
                    recl_ssurgo_csv.close()

                    out_reclass = ReclassByTable(out_ssurgo_file,out_ssurgo_dir+os.sep+st+'.csv', "FROM", "TO", "VALUE", "DATA")
                    out_reclass.save(recl_ssurgo_file)
                except:
                    logging.info(arcpy.GetMessages())
                    delete_temp_files(files_to_delete)
            else:
                logging.info('File present: '+recl_ssurgo_file)

    # Create new raster mosaic
    if not(arcpy.Exists(merged_soil_folder+os.sep+merged_soil_file)):
        list_sgo_files = ';'.join(list_sgo_files)  
        try:                  
            arcpy.MosaicToNewRaster_management(list_sgo_files,merged_soil_folder,merged_soil_file, "",\
                                                "32_BIT_SIGNED", "", "1", "LAST","FIRST")
            arcpy.BuildRasterAttributeTable_management(merged_soil_folder+os.sep+merged_soil_file, "Overwrite")
            logging.info('Created Mosaiced raster '+merged_soil_folder+os.sep+merged_soil_file)
        except:
            logging.info(arcpy.GetMessages())
            delete_temp_files(files_to_delete)
    else:
        logging.info('File present: '+merged_soil_folder+os.sep+merged_soil_file)
    delete_temp_files(files_to_delete)

def run_merge_ssurgo_rasters(): 
    pool = multiprocessing.Pool(constants.max_threads)
    pool.map(merge_ssurgo_rasters,constants.list_st)
    pool.close()
    pool.join()    
    logging.info('Done!')

if __name__ == "__main__":
    run_merge_ssurgo_rasters()
    logging.info('Done!')
