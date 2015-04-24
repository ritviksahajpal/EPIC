##################################################################
# seimf.py July 2011
# ritvik sahajpal (ritvik@umd.edu)
# Creates a combined raster based on seimf approach from ssurgo, dem
# ndhd, dem and cdl based crop rotation data.
# Uses dbfpy library from http://sourceforge.net/projects/dbfpy/files/
##################################################################
import os, sys, logging, pdb, getopt, glob, zipfile, arcpy, csv, time, multiprocessing
from arcpy.sa import *
from dbfpy import dbf
import constants

# ArcGIS constants
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput = True
arcpy.env.extent = "MAXOF"

def seimf(state):
    inp_rasters = '"' # contains the list of rasters which are to be merged together to create the SEIMF geodatabase
    logging.info(state)

    sgo_dir = constants.epic_dir+os.sep+'Data'+os.sep+'ssurgo'+os.sep+state+os.sep
    lu_dir  = constants.epic_dir+os.sep+'Data'+os.sep+'LU'+os.sep+state+os.sep
    cnt_dir = constants.base_dir+os.sep+'Data'+os.sep+'GIS'+os.sep+'county'+os.sep    

    out_dir = constants.epic_dir+os.sep+'SEIMF'+os.sep
    constants.make_dir_if_missing(out_dir)

    # Combine SSURGO and land use data
    out_raster = out_dir+os.sep+'SEIMF_'+state
    if(not(arcpy.Exists(out_raster))):
        inp_rasters += sgo_dir+os.sep+state+'_ssurgo'+'; '+lu_dir+\
                       os.sep+'open_'+str(constants.year)+'_'+state+'"'
        try:
            out_combine  = Combine(inp_rasters)
            out_combine.save(out_raster)
            logging.info('Combined rasters to SEIMF raster '+out_raster)
        except:
            logging.info(arcpy.GetMessages())
    else:
        logging.info('File present: '+out_raster)

    # Compute centroid of each HSMU using zonal geometry
    zgeom_dbf  = out_dir+os.sep+state+'.dbf'
    reproj_ras = out_dir+os.sep+state+'_reproj'
    if(not(arcpy.Exists(zgeom_dbf))):
        try:
            cdl_spatial_ref = arcpy.SpatialReference(4269)
            arcpy.ProjectRaster_management(out_raster, reproj_ras, cdl_spatial_ref)

            out_zgeom = ZonalGeometryAsTable(reproj_ras, 'VALUE', zgeom_dbf)
            logging.info('Computed zonal geometry '+zgeom_dbf)

            arcpy.JoinField_management(out_raster,"VALUE",zgeom_dbf,"VALUE","XCENTROID;YCENTROID")
            logging.info('JoinField_management '+out_raster)
        except:
            logging.info(arcpy.GetMessages())
    else:
        logging.info('File present: '+zgeom_dbf)

    # XCENTROID YCENTROID WI_SSURGO OPEN_2013_WI
    # Iterate through the zonal geometry dbf
    #with arcpy.da.SearchCursor(zgeom_dbf, ['VALUE',constants.MUKEY]) as cursor:
    #    for row in cursor:
    # Create EPIC site file
    # Get closest NARR lat-lon
    # Create EPICRUN.dat
    # 
    # 
    # df.drop_duplicates(cols='mukey')    

def parallelize_seimf():
    pool = multiprocessing.Pool(constants.max_threads)
    pool.map(seimf,constants.list_st)
    pool.close()
    pool.join()    
    logging.info('Done!')

if __name__ == '__main__':
    parallelize_seimf()

#def delete_temp_files(files_to_delete):
#    # Delete all the temporary files
#    for i in range(len(files_to_delete)):
#        # print 'Deleting: '+files_to_delete[i]
#        try:
#            arcpy.Delete_management(files_to_delete[i],"")
#        except:
#            print arcpy.GetMessages()

#    del(files_to_delete[:])

#cnt_fl     = cnt_dir+os.sep+state+'.shp'
#reproj_fl  = out_dir+os.sep+state+'_reproj.shp'
#mod_cnt_fl = out_dir+os.sep+state+'_mod.shp'
#out_cnt_fl = out_dir+os.sep+state+'_out'
#if(not(arcpy.Exists(out_cnt_fl))):
#    try:
#        cdl_spatial_ref = arcpy.SpatialReference(4269)
#        arcpy.Project_management(cnt_fl, reproj_fl, cdl_spatial_ref)

#        arcpy.CopyFeatures_management(reproj_fl, mod_cnt_fl)

#        arcpy.AddField_management(mod_cnt_fl, "X", "FLOAT")
#        arcpy.AddField_management(mod_cnt_fl, "Y", "FLOAT")
#        logging.info('AddField_management '+mod_cnt_fl)
        
#        # Centroid property returns a string with x and y separated by a space
#        x_exp = "float(!SHAPE.CENTROID@DECIMALDEGREES!.split()[0])"
#        y_exp = "float(!SHAPE.CENTROID@DECIMALDEGREES!.split()[1])"

#        arcpy.CalculateField_management(mod_cnt_fl, "X", x_exp, "PYTHON")
#        arcpy.CalculateField_management(mod_cnt_fl, "Y", y_exp, "PYTHON")
#        logging.info('CalculateField_management '+mod_cnt_fl)

#        arcpy.FeatureToRaster_conversion(mod_cnt_fl, "FIPS", out_cnt_fl)
#        arcpy.JoinField_management(out_cnt_fl, "FIPS", mod_cnt_fl, "FIPS", "")
#        logging.info('JoinField_management '+out_cnt_fl)
#    except:
#        logging.info(arcpy.GetMessages())
#else:
#    logging.info('File present: '+out_cnt_fl)

## Create a dictionary containing the full state name as well as its abbreviation
#state_names = {}
#states = csv.reader(open(states_file), delimiter=',')
#for row in states:
#    #state_names['ia'] = ['iowa']
#    state_names[row[1]] = [row[0]]

## Start the clock
#start_time = time.clock()


## Iterate over all the states contained in the dictionary state_names
#for state in state_names.keys():
#    inp_rasters ='"' # contains the list of rasters which are to be merged together to create the SEIMF geodatabase
#    in_dem_file = in_dem_dir+os.sep+'us_dem_pr' # Used in zonal statistics to compute average elevation in each watershed 
#    in_cdl_file = glob.glob(in_cdl_dir+os.sep+state+os.sep+'all_'+state+'_*yrs')[0] # CDL based crop rotation raster

#    out_combined_dir = out_dir+os.sep+COMBINED+os.sep+state # Output directory to store merged SSURGO files for each state
#    if not os.path.exists(out_combined_dir): # Create output directory if does not exist already
#        os.makedirs(out_combined_dir)
#    files_to_delete = []       # Temporary files which will be deleted at the end

#    # DBF tables needed for SEIMF
#    HUelev_table   = dbf.Dbf(out_combined_dir+os.sep+'HUelev.dbf', new=True)
#    HU10_table     = dbf.Dbf(out_combined_dir+os.sep+'HU10.dbf', new=True)
#    HUlonlat_table = dbf.Dbf(out_combined_dir+os.sep+'HUlonlat.dbf', new=True)
#    County_table   = dbf.Dbf(out_combined_dir+os.sep+'County.dbf', new=True)
#    Com_table      = dbf.Dbf(out_combined_dir+os.sep+'Com.dbf', new=True)
    
#    HUelev_table.addField(("VALUE",'N',20),("HUC_10",'N',20),("Elev",'N',20,20))
#    HUlonlat_table.addField(("HUC_10",'N',20),("Lon",'N',20,20),("Lat",'N',20,20))
#    County_table.addField(("VALUE",'N',20),("FIPS",'N',20),("X",'N',20,20),("Y",'N',20,20))
#    HU10_table.addField(("VALUE",'N',20),("HUC_10",'N',20))
#    Com_table .addField(("VALUE",'N',20),("COUNT",'N',20),("COUNTY",'N',20),("10DIGIT",'N',20),("SSURGO",'N',20),("CDL",'N',20))
    
#    # We use the spatial reference information from the CDL to reproject (if needed) the other data layers
#    cdl_spatial_ref = arcpy.CreateSpatialReference_management(in_cdl_file, "", "", "", "", "", "0")

#    ############################################
#    #
#    #Processing County Boundary Files
#    #They SHOULD already be in the correct geographic projection 
#    ############################################
#    print 'STEP 1: Processing County Boundary Files for '+state
#    logging.debug('STEP 1: '+state)
#    # in_county_dir= 'W:\SEIMF\COUNTY\'
#    in_county_file = in_county_dir+os.sep+state+'.shp'

#    out_county_dir = out_dir+os.sep+BOUNDARY+os.sep+state
#    if not os.path.exists(out_county_dir):
#        os.makedirs(out_county_dir)
#    out_county_file = out_county_dir+os.sep+state+BOUNDARY
#    mod_county_file = out_county_dir+os.sep+state+'_mod.shp' # mod or modified to include X and Y coords of centroid of watershed
    
#    try:
#        arcpy.CopyFeatures_management(in_county_file, mod_county_file)

#        arcpy.AddField_management(mod_county_file, "X", "LONG", 18, 11)
#        arcpy.AddField_management(mod_county_file, "Y", "LONG", 18, 11)
        
#        # Centroid property returns a string with x and y separated by a space
#        xExpression = "float(!SHAPE.CENTROID!.split()[0])"
#        yExpression = "float(!SHAPE.CENTROID!.split()[1])"
        
#        arcpy.CalculateField_management(mod_county_file, "X", xExpression, "PYTHON")
#        arcpy.CalculateField_management(mod_county_file, "Y", yExpression, "PYTHON")
        
#        arcpy.FeatureToRaster_conversion(mod_county_file, "FIPS", out_county_file, CDL_RESOLUTION)
#        arcpy.JoinField_management(out_county_file, "FIPS", mod_county_file, "FIPS", "")

#        # Delete the intermediary reprojected file and the file with X,Y calculated
#        files_to_delete.append(mod_county_file)

#        # Write the county dbf file
#        cur = arcpy.SearchCursor(out_county_file)
#        row=cur.next()
#        while row:
#            rec = County_table.newRecord()
#            print row.getValue("FIPS"),row.getValue("X"),row.getValue("Y")
#            rec["VALUE"] = int(row.getValue("VALUE"))
#            rec["FIPS"] = float(row.getValue("FIPS"))
#            rec["X"] = float(row.getValue("X"))
#            rec["Y"] = float(row.getValue("Y"))
#            rec.store()
#            row = cur.next()
        
#        County_table.close()
#    except:
#        print 'ERROR: STEP1'
#        print arcpy.GetMessages()
#        logging.debug('ERROR STEP 1: '+state)
#        any_errors = True
#        delete_temp_files(files_to_delete)

#    inp_rasters += out_county_file+"; "

#    ############################################
#    #
#    #Processing Watershed Boundary Files
#    #
#    ############################################    
#    print 'STEP 2: Processing Watershed Boundary Files for '+state
#    logging.debug('STEP 2: '+state)
#    #in_ndhd_dir = 'W:\SEIMF\10digit\shapefiles'
#    in_ndhd_file = in_ndhd_dir+os.sep+state+'.shp' 

#    out_ndhd_dir = out_dir+os.sep+WSHD+os.sep+state
#    if not os.path.exists(out_ndhd_dir):
#        os.makedirs(out_ndhd_dir)
#    mod_ndhd_file = out_ndhd_dir+os.sep+state+'_mod.shp' # mod or modified to include X and Y coords of centroid of watershed
#    reproj_ndhd_file = out_ndhd_dir+os.sep+state+'_reproj.shp' # reprojected to CDL geographic projection
#    out_ndhd_file = out_ndhd_dir+os.sep+state+WSHD # converted to raster
#    out_huelev_file = out_ndhd_dir+os.sep+state+'HUelev' # zonal stats used to compute mean elevation for each watershed
    
#    # Adding X and Y parameters
#    print '\tSTEP 2.0: Adding X and Y Centroids to watershed file'
#    logging.debug('STEP 2.0: '+state)
#    try:
#        arcpy.CopyFeatures_management(in_ndhd_file, mod_ndhd_file)
        
#        arcpy.AddField_management(mod_ndhd_file, "X", "LONG", 18, 11)
#        arcpy.AddField_management(mod_ndhd_file, "Y", "LONG", 18, 11)
        
#        # Centroid property returns a string with x and y separated by a space
#        xExpression = "float(!SHAPE.CENTROID!.split()[0])"
#        yExpression = "float(!SHAPE.CENTROID!.split()[1])"
        
#        arcpy.CalculateField_management(mod_ndhd_file, "X", xExpression, "PYTHON")
#        arcpy.CalculateField_management(mod_ndhd_file, "Y", yExpression, "PYTHON")

#        print '\tSTEP 2.1: Reprojecting watershed file'
#        arcpy.Project_management(mod_ndhd_file, reproj_ndhd_file, cdl_spatial_ref)
        
#        print '\tSTEP 2.2: Converting watershed file to raster'
#        try:
#           arcpy.FeatureToRaster_conversion(reproj_ndhd_file, "HUC_10", out_ndhd_file, CDL_RESOLUTION)
#        except:
#            print arcpy.GetMessages()
#        # Process: Zonal Statistics as Table...
#        print '\tSTEP 2.3: Computing Zonal Statistics'
#        try:
#           out_zsat = ZonalStatisticsAsTable(in_ndhd_file, "HUC_10", in_dem_file, out_huelev_file, "DATA")
#        except:
#            print arcpy.GetMessages()

#        # Delete the intermediary reprojected file and the file with X,Y calculated
#        files_to_delete.append(mod_ndhd_file)
#        files_to_delete.append(reproj_ndhd_file)
        
#        # Write the HUelev and HUlonlat tables
#        cur = arcpy.SearchCursor(out_huelev_file)
#        row=cur.next()
#        while row:
#            rec = HUelev_table.newRecord()
#            rec["VALUE"] = int(row.getValue("ZONE-CODE"))
#            rec["HUC_10"] = int(row.getValue("HUC_10"))
#            rec["Elev"] = float(row.getValue("MEAN"))
#            rec.store()

#            rec10 = HU10_table.newRecord()
#            rec10["VALUE"] = int(row.getValue("ZONE-CODE"))
#            rec10["HUC_10"] = int(row.getValue("HUC_10"))
#            rec10.store()
#            row = cur.next()
            
#        HU10_table.close()        
#        HUelev_table.close()

#        cur = arcpy.SearchCursor(mod_ndhd_file)
#        row=cur.next()
#        while row:
#            rec = HUlonlat_table.newRecord()
#            print row.getValue("HUC_10"),row.getValue("X"),row.getValue("Y")
#            rec["HUC_10"] = int(row.getValue("HUC_10"))
#            rec["Lon"] = float(row.getValue("X"))
#            rec["Lat"] = float(row.getValue("Y"))
#            rec.store()
#            row = cur.next()

#        HUlonlat_table.close()
#    except:
#        any_errors = True
#        print 'ERROR: STEP2'
#        print arcpy.GetMessages()
#        logging.debug('ERROR STEP 2: '+state)
#        #delete_temp_files(files_to_delete)
    
#    inp_rasters += out_ndhd_file+'; '

#    ############################################
#    #
#    #Processing SSURGO Files
#    #
#    ############################################
#    print 'STEP 3: Processing SSURGO Files for '+state
#    logging.debug('STEP 3: '+state)    
#    # in_ssurgo_dir = 'W:\SEIMF\SSURGO\'
#    #soils_dir  = os.listdir(in_ssurgo_dir+os.sep+state)
#    to_merge_ssurgo_files = [] # SSURGO files which need to be merged

#    out_ssurgo_dir = out_dir+os.sep+SOIL+os.sep+state # Output directory to store merged SSURGO files for each state
#    if not os.path.exists(out_ssurgo_dir+os.sep+CATALOG): # Create output directory if does not exist already
#        os.makedirs(out_ssurgo_dir+os.sep+CATALOG)

#    for j in range(1):
#        # The reclassification is done to make the VALUE equal to the MUKEY
#        recl_ssurgo_csv = open(out_ssurgo_dir+os.sep+state+'.csv', 'wb')
#        recl_ssurgo_csv.write('FROM, TO, VALUE\n')
#        recl_ssurgo_csv.flush()        
#        # Iterate through each of the soil files for a given state
#        # in_ssurgo_file = glob.glob(in_ssurgo_dir+os.sep+state+os.sep+soils_dir[j]+os.sep+'spatial'+os.sep+'soilmu_a_*.shp')[0]
#        # reproj_file is the name of the reprojected ssurgo file
#        # reproj_file = out_ssurgo_dir+os.sep+os.path.basename(in_ssurgo_file[:-4])+'_reproj.shp'
#        # out_ssurgo_file is the reprojected and reclassified (to CDL resolution) SSURGO file
#        out_ssurgo_file = out_ssurgo_dir+os.sep+state+os.sep+state+'ssurgo'
#        # reclass_ssurgo_file has the MUKEY as the VALUE column
#        recl_ssurgo_file = out_ssurgo_dir+os.sep+state+os.sep+state+'_recl'
#        # Append the files to the list of ssurgo files to be merged to form one raster 
#        to_merge_ssurgo_files.append(recl_ssurgo_file)
#        merged_soil_folder = out_ssurgo_dir
#        merged_soil_file   = state+SOIL

#        print '\tSTEP 3'+'.'+str(j)+': Shapefile '+os.path.basename(state)+\
#                ' is being reprojected, reclassified and converted to raster '+os.path.basename(out_ssurgo_file)
        
#        try:
#            recl_ssurgo_csv = open(out_ssurgo_dir+os.sep+state+'.csv', 'a+')
#            cur = arcpy.SearchCursor(out_ssurgo_file)
#            row=cur.next()
#            while row:
#                recl_ssurgo_csv.write(str(row.getValue("VALUE"))+', '+str(row.getValue("VALUE"))+', '+row.getValue("MUKEY")+'\n')
#                row = cur.next()
#            recl_ssurgo_csv.close()

#            out_reclass = ReclassByTable(out_ssurgo_file,out_ssurgo_dir+os.sep+state+'.csv', "FROM", "TO", "VALUE", "DATA")
#            out_reclass.save(recl_ssurgo_file)
            
#            files_to_delete.append(out_ssurgo_file)
#            files_to_delete.append(recl_ssurgo_file)
#            files_to_delete.append(reproj_file)
#        except:
#            any_errors = True
#            print 'ERROR: STEPS 3.1...'
#            print arcpy.GetMessages()
#            logging.debug('ERROR STEP 3: '+state)
#            delete_temp_files(files_to_delete)

#        delete_temp_files(files_to_delete)
        
#    inp_rasters += merged_soil_folder+os.sep+merged_soil_file+"; "
#    ############################################
#    #
#    #Combining all raster files
#    #
#    ############################################
#    print 'STEP 4: Combining all raster files for '+state
#    logging.debug('ESTEP 4: '+state)
#    out_raster = out_combined_dir+os.sep+COM
#    inp_rasters += in_cdl_file+'"'

#    try:
#        print inp_rasters
#        out_combine = Combine(inp_rasters)
#        out_combine.save(out_raster)
        
#        cur = arcpy.SearchCursor(out_raster)
#        row=cur.next()
#        while row:
#            rec = Com_table.newRecord()
#            rec["VALUE"] = int(row.getValue("VALUE"))
#            rec["COUNT"] = int(row.getValue("COUNT"))
#            rec["COUNTY"] = int(row.getValue(state+"COUNTY"))
#            rec["10DIGIT"] = int(row.getValue(state+"10DIGIT"))
#            rec["SSURGO"] = int(row.getValue(state+"SSURGO"))
#            rec["CDL"] = int(row.getValue(os.path.basename(in_cdl_file)))
#            rec.store()
#            row = cur.next()

#        Com_table.close()
#    except:
#        any_errors = True
#        print 'ERROR: STEP4'
#        print arcpy.GetMessages()
#        delete_temp_files(files_to_delete)
    
#    if any_errors:
#        print 'CHECK FOR ERRORS IN GEOPROCESSING!!!'
    
#    delete_temp_files(files_to_delete)
    
#    print "Time to process for "+state+": " +str(time.clock() - start_time), "seconds"

#print 'DONE'

#if __name__ == "__main__":
#    merge_ssurgo_rasters()