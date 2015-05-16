################################################################
# September 8, 2014
# OpenLandsConversion.py
# email: ritvik@umd.edu
#
#################################################################
import os, time, pdb, operator, csv, glob, logging, shutil, arcpy, datetime, numpy, sys, pandas, multiprocessing
from dbfpy import dbf
from arcpy.sa import *
from itertools import groupby, combinations, combinations_with_replacement
from collections import Counter
import constants

# Arcpy constants
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput= True
arcpy.env.extent         = "MAXOF"

###############################################################################
#
#
#
#
###############################################################################
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

###############################################################################
#
#
#
#
###############################################################################
def backup_source_code(out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    try:
        shutil.copy(os.path.realpath(__file__),out_dir)
    except:
        logging.info("WARNING: could not save source code file")

###############################################################################
#
#
#
#
###############################################################################
def output_as_matrix(mat, name):
    df_t = mat.transpose().reset_index()
    # Determine row and column names
    df_t['col_name'] = df_t['index'].str.split('_').map(lambda x: x[1])
    df_t['row_name'] = df_t['index'].str.split('_').map(lambda x: x[0])

    # Create matrix
    df_t = df_t.pivot(index='row_name', columns='col_name', values=0)
    
    # Drop names
    df_t.index.name = None
    df_t.columns.name = None
    
    # Fill Nan's by 0
    df_t.fillna(0,inplace=True)
    
    # Output both matrix as well as net values matrix
    net_df_t = (df_t-df_t.T)+numpy.diag(numpy.diag(df_t))
    df_t.to_csv(constants.out_dir+name+'.csv')
    net_df_t.to_csv(constants.out_dir+'Net_'+name+'.csv')

###############################################################################
#
#
#
#
###############################################################################
def check_if_ag(val):
    if(val==constants.WHEAT or val==constants.CORN or val==constants.SOY or val==constants.OTHER):
        return True
    else:
        return False
    
###############################################################################
#
#
#
#
###############################################################################
def year_of_conversion(row):
    idx_last_cult = 0
    conv_field    = 'Ignore'

    # Check if there are any open lands
    if(row.count(constants.OPEN)):
        # If there are any open lands, check if there is conversion in last year
        # Also, 1st year should be OPEN                            
            if (constants.USE_INTERIM or row[0]==constants.OPEN):
                if(row[len(row)-1] != constants.OPEN):
                    # Find out what was final conversion
                    if(row[len(row)-1] == constants.CORN):
                        conv_field = 'Corn'
                    elif(row[len(row)-1] == constants.WHEAT):
                        conv_field = 'Wheat'
                    elif(row[len(row)-1] == constants.SOY):
                        conv_field = 'Soy'
                    elif(row[len(row)-1] == constants.FOREST):
                        conv_field = 'Forest'     
                    elif(row[len(row)-1] == constants.URBAN):
                        conv_field = 'Urban'
                    elif(row[len(row)-1] == constants.WATER):
                        conv_field = 'Water'
                    else:
                        conv_field = 'Other'   
                elif(not(constants.USE_INTERIM) and row[len(row)-1]==constants.OPEN): #Both first and last LU are OPEN
                    return(-1,conv_field)                                                                                 
                # Find out year of conversion from open land
                idx_last_cult = len(row) - 1 - row[::-1].index(constants.OPEN)
                
                return (constants.START_YEAR+idx_last_cult+1,conv_field)

    return (-1,conv_field)
    
###############################################################################
#
#
#
#
###############################################################################
def consecutive_cropping(row,crop_id):
    max_run = 0
    total_count = row.count(crop_id)
    
    if total_count:
        max_run = max(sum(1 for _ in g) for k, g in groupby(row) if k==crop_id)
    
    return max_run

###############################################################################
#
#
#
#
###############################################################################
def identify_monoculture(row):
    if(len(set(row)) == 1):
        return 1
    elif(Counter(set(row))==Counter(constants.CORN_SOY)):# Counter gets the unique values in a list
        return 1
    else:
        return 0

###############################################################################
#
#
#
#
###############################################################################
def number_yrs_after_open(row):    
    num_yrs = 0
    cult_yr = 0
    
    if(row.count(constants.OPEN)):
        if(constants.USE_INTERIM or row[0]==constants.OPEN):
            # Find the last year of open land
            last_yr = row[::-1].index(constants.OPEN)
            
            # Determine the number of years of cultivation after that
            if(last_yr > 0):
                for j in constants.CULTIVATED:
                    cult_yr += row[-last_yr:].count(j)    
                
                if(cult_yr > 0):
                    num_yrs  = last_yr
        
    return cult_yr, num_yrs

###############################################################################
#
#
#
#
###############################################################################
def any_cultivation(row):
    for j in constants.CULTIVATED:
        if(j in row):
            return True
    
    return False

def output_raster_attribute_to_csv(reg,state,ras,TITL,replace):
    state_dir = constants.out_dir+os.sep+state+os.sep
    out_csv   = state_dir+TITL+reg+'_'+state+'.csv'
    fields    = "*"
      
    if arcpy.Exists(out_csv) and not(replace):
        pass
    else:
        try:  
            lst_flds = arcpy.ListFields(ras)  
            header = ''  
            for fld in lst_flds:  
                header += "{0},".format(fld.name)  
            
            # Add region and state to header
            header +=  "{0},".format('REGION')
            header +=  "{0},".format('STATE')

            if len(lst_flds) != 0:    
                f = open(out_csv,'w')  
                  
                f.write(header+'\n')  
                with arcpy.da.SearchCursor(ras, fields) as cursor:  
                    for row in cursor:  
                        f.write(str(row).replace("(","").replace(")","")+','+reg+','+state+'\n')  
                f.close()
      
        except:  
            logging.info('\t '+ras+" - is not integer or has no attribute table")  

    logging.info('\tOutputting csv for region '+reg+' in state '+state)
    return out_csv    
      
###############################################################################
#
#
#
#
###############################################################################
def join_csv(reg,state,ras,out_csv,replace):
    state_dir    = constants.out_dir+os.sep+state+os.sep
    out_CR       = state_dir+state+'_cr'
    
    if not(replace):
        pass
    else:
        try:
            arcpy.CopyRows_management(out_csv,out_CR)        
            arcpy.BuildRasterAttributeTable_management(ras, "Overwrite")
            arcpy.JoinField_management(ras,"VALUE",out_CR,"VALUE","")
            logging.info('\tJoining region ' +reg+' for state '+state)
        except:
            logging.info(arcpy.GetMessages())
            
    return ras

###############################################################################
#
#
#
#
###############################################################################
def extract_by_mask(state,extract_comb,titl,replace):
    state_dir = constants.out_dir+os.sep+state+os.sep
    list_ras  = []
    for reg in constants.REGION:
        ext_ras  = state_dir+titl+reg+'_'+state+'_'+str(constants.START_YEAR)[2:]+'_'+str(constants.END_YEAR)[2:]
        vec_mask = constants.base_dir+os.sep+'Data\\GIS\\Lake_States_Outline'+os.sep+reg+'_'+'LakeStates.shp'
        list_ras.append(ext_ras)
        
        if arcpy.Exists(ext_ras) and not(replace):
            pass
        else:
            try:
                arcpy.gp.ExtractByMask_sa(extract_comb,vec_mask,ext_ras)
            except:
                logging.info(arcpy.GetMessages())
        
        logging.info('\tExtracting for '+reg+' in state '+state)
        
    return list_ras

###############################################################################
#
#
#
#
###############################################################################
def extract_LU_change(state,ras,replace):
    state_dir = constants.out_dir+os.sep+state+os.sep
    ext_ras   = state_dir+'LU_'+state+'_'+str(constants.START_YEAR)[2:]+'_'+str(constants.END_YEAR)[2:]
    where     = constants.CONVERSION+" > -1" 

    if arcpy.Exists(ext_ras) and not(replace):
        pass
    else:
        #arcpy.Copy_management(ras,ext_ras)
        try:
            att_extract = ExtractByAttributes(ras,where) 
            att_extract.save(ext_ras)
        except:
            logging.info(arcpy.GetMessages())

    logging.info('\tRemove no LU pixels for state '+state)
    return ext_ras

###############################################################################
#
#
#
#
###############################################################################
def filter_and_project_raster(reg,state,ras,replace):    
    filtered_state =  constants.out_dir+os.sep+state+os.sep+'f_'+reg+'_'+state+'_'+str(constants.START_YEAR)[2:]+'_'+str(constants.END_YEAR)[2:]
    tmp_ras        =  constants.out_dir+os.sep+state+os.sep+'t_'+reg+'_'+state+'_'+str(constants.START_YEAR)[2:]+'_'+str(constants.END_YEAR)[2:]
    
    if arcpy.Exists(filtered_state) and not(replace):
        pass
    else:
        try:
            where = "COUNT > "+str(constants.FILTER_SIZE)
            att_extract = ExtractByAttributes(ras,where) 
            att_extract.save(tmp_ras)
        except:
            logging.info(arcpy.GetMessages())

        try:
            out_set_null = SetNull(Lookup(RegionGroup(tmp_ras,"","","NO_LINK",""),"Count") <= constants.FILTER_SIZE,tmp_ras)
            out_set_null.save(filtered_state)

            #arcpy.Copy_management(ras,filtered_state)
            
            ####arcpy.BuildRasterAttributeTable_management(ras,"NONE")
            # Process: Extract by Attributes
            ####arcpy.gp.ExtractByAttributes_sa(ras,"COUNT > 9",tmp_ras)
            ####arcpy.BuildRasterAttributeTable_management(tmp_ras,"NONE")
            ####arcpy.Copy_management(tmp_ras,filtered_state)            
            # Process: Build Raster Attribute Table
            ####arcpy.BuildRasterAttributeTable_management(filtered_state, "NONE")
                        
            # Reproject
            dsc = arcpy.Describe(ras)
            coord_sys = dsc.spatialReference
            arcpy.DefineProjection_management(filtered_state,coord_sys)
        except:
            logging.info(arcpy.GetMessages())
    
    logging.info('\t Filtering small pixels from state '+state)
    return filtered_state

###############################################################################
#
#
#
#
###############################################################################
def sieve(state,extract_comb):
    filtered_state =  constants.out_dir+os.sep+state+os.sep+'fs_'+reg+'_'+state+'_'+str(constants.START_YEAR)[2:]+'_'+str(constants.END_YEAR)[2:]#constants.out_dir+os.sep+state+os.sep+'final_'+state
    
    try:
        tmp1 = RegionGroup(extract_comb, "EIGHT", "WITHIN", "NO_LINK", "") 
        query = "VALUE > " + constants.FILTER_SIZE
        tmp2 = ExtractByAttributes(tmp1, query)
        
        out_raster = Nibble(extract_comb, tmp2)
        out_raster.save(filtered_state)
        
        # Reproject
        dsc = arcpy.Describe(ras)
        coord_sys = dsc.spatialReference
        arcpy.DefineProjection_management(filtered_state,coord_sys)
    except:
        logging.info(arcpy.GetMessages())
        
    logging.info('\t Filtering small pixels from state '+state)
    return filtered_state

###############################################################################
#
#
#
#
###############################################################################
def filter_polygon(state,extract_comb):
    poly_1 = constants.out_dir+os.sep+state+os.sep+'poly_1.shp'
    poly_2 = constants.out_dir+os.sep+state+os.sep+'poly_2.shp'
    
    arcpy.RasterToPolygon_conversion(extract_comb, poly_1, "NO_SIMPLIFY", "VALUE")
    arcpy.CalculateAreas_stats(poly_1,poly_2)
 
###############################################################################
#
#
#
#
###############################################################################   
def identify_no_change_pixels(state,ras,replace):
    state_dir   = constants.out_dir+os.sep+state+os.sep
    out_csv     = constants.shared_dir+state+'_not_filtered.csv'#state_dir+state+'_not_filtered.csv'
    field_names = []
    
    if arcpy.Exists(out_csv) and not(replace):
        pass
    else:
        with open(out_csv,'wb') as f:
            w = csv.writer(f)

            try:
                arcpy.AddField_management(ras,constants.CONVERSION,"LONG")
                arcpy.AddField_management(ras,'YR_CONVERSION',"LONG")
                arcpy.AddField_management(ras,'CONV_FIELD',"TEXT")
                arcpy.AddField_management(ras,'CULTIVATED',"LONG")
                arcpy.AddField_management(ras,'OPEN',"LONG")                
                arcpy.AddField_management(ras,'CORN',"LONG")
                arcpy.AddField_management(ras,'SOY',"LONG")
            except:
                logging.info(arcpy.GetMessages())                        
                            
            cursor = arcpy.UpdateCursor(ras)
            # Lets make a list of all of the fields in the table
            fields = arcpy.ListFields(ras)    
            field_names = [field.name for field in fields]
            # Write all field names to the output file
            w.writerow(field_names)
                        
            for row in cursor:
                land_use_trend = []
                for j in range(constants.START_YEAR, constants.END_YEAR+1):            
                    land_use_trend.append(row.getValue('RECL_'+state.upper()+'_'+str(j)))
                if(identify_monoculture(land_use_trend)):
                    row.setValue(constants.CONVERSION,-1)
                elif(not(any_cultivation(land_use_trend))):
                    row.setValue(constants.CONVERSION,0)
                else:
                    row.setValue(constants.CONVERSION,1)

                num_consecutive_corn = consecutive_cropping(land_use_trend,constants.CORN)
                num_consecutive_soy  = consecutive_cropping(land_use_trend,constants.SOY)
                cult_yr, num_yrs     = number_yrs_after_open(land_use_trend)
                year, conv_field     = year_of_conversion(land_use_trend)
                
                row.setValue('CULTIVATED',cult_yr)
                row.setValue('OPEN',num_yrs)
                row.setValue('YR_CONVERSION',year)
                row.setValue('CONV_FIELD',conv_field)
                                
                if(num_consecutive_corn):
                    row.setValue('CORN',num_consecutive_corn)
                if(num_consecutive_soy):
                    row.setValue('SOY',num_consecutive_soy)
                    
                cursor.updateRow(row)
                field_vals = [row.getValue(field.name) for field in fields]
                w.writerow(field_vals)
                
                #row = cursor.next()
    
    #arcpy.ExportXYv_stats(ras,field_names,"COMMA",constants.shared_dir+state+'_all.csv',"ADD_FIELD_NAMES")
    logging.info('\tIdentifying monoculture and no cultivation pixels in state '+state)
    return out_csv

###############################################################################
#
#
#
#
###############################################################################
def erase_PAD(state,ras,replace):
    # Process: Erase
    
    pad_state     = constants.pad_dir+'PAD-US_'+state+'\\PADUS1_3_'+state+'.gdb\\PADUS1_3'+state    
    pad_out_dir   = constants.pad_dir+'output\\'+state+os.sep
    bound_out_dir = constants.bound_dir+'output\\'+state+os.sep
    state_dir     = constants.out_dir+os.sep+state+os.sep
    
    constants.make_dir_if_missing(pad_out_dir)
    constants.make_dir_if_missing(bound_out_dir)
    constants.make_dir_if_missing(state_dir)
    
    select_state  = bound_out_dir+state+'.shp'
    erased_pad    = pad_out_dir+state+'.shp'
    extract_comb  = state_dir+'ext_'+state+'_'+str(constants.START_YEAR)[2:]+'_'+str(constants.END_YEAR)[2:]

    #
    if arcpy.Exists(select_state) and not(replace):
        pass
    else:
        where = '"STATE_ABBR" = ' + "'%s'" %state.upper()
        try:
            arcpy.Select_analysis(constants.BOUNDARIES,select_state,where)
        except:
            logging.info(arcpy.GetMessages())

    #
    if arcpy.Exists(erased_pad) and not(replace):
        pass
    else:
        try:
            arcpy.Erase_analysis(select_state,pad_state,erased_pad, "")
        except:
            logging.info(arcpy.GetMessages())

    #
    if arcpy.Exists(extract_comb) and not(replace):
        pass
    else:
        try:
            # Create bounding box from polygon (xmin, ymin, xmax, ymax)
            #desc = arcpy.Describe(erased_pad)
            #rectangle = "%s %s %s %s" % (desc.extent.XMin, desc.extent.YMin, desc.extent.XMax,   desc.extent.YMax)
            
            #arcpy.Clip_management(ras,rectangle,extract_comb,erased_pad,"#","ClippingGeometry")
            arcpy.gp.ExtractByMask_sa(ras,erased_pad,extract_comb)
        except:
            logging.info(arcpy.GetMessages())

    logging.info('\t Erasing PAD from state '+state)
    return extract_comb

###############################################################################
# create_zonal_state
#
#
#
###############################################################################
def create_zonal_state(state,ras,yr):
    # Perform lookup on COUNT column, since we want to perform zonal stat on area/count
    try:
        lu_tmp = Lookup(ras,'COUNT')        
        lu_tmp.save(constants.out_dir+os.sep+state+os.sep+'LupOp_'+str(yr)+'_'+state)

        in_zone_data = constants.base_dir+'Data\\GIS\\UScounties\\LakeStateCounty.shp'        
        out_zsat     = ZonalStatisticsAsTable(in_zone_data,'FIPS',constants.out_dir+os.sep+state+os.sep+'LupOp_'+str(yr)+'_'+state,\
                                                constants.out_dir+os.sep+state+os.sep+'Open_'+str(yr)+'_'+state+'_zsat.dbf', "DATA", "SUM")              
        dbf_to_csv(constants.out_dir+os.sep+state+os.sep+'Open_'+str(yr)+'_'+state+'_zsat.dbf')
    except:
        logging.info(arcpy.GetMessages())

    logging.info('Zonal stat as table... '+constants.out_dir+os.sep+state+os.sep+'Open_'+str(yr)+'_'+state+'_zsat.dbf')

###############################################################################
# reclassify_and_combine
#
#
#
###############################################################################
def reclassify_and_combine(state,state_lcc,state_cdl_files,range_of_yrs,replace):
    to_comb_rasters = []
    end_open_ras    = constants.epic_dir+os.sep+state+os.sep+'Open_'+str(constants.END_YEAR)+'_'+state # OPEN_20xx_<state_name>
    start_open_ras  = constants.epic_dir+os.sep+state+os.sep+'Open_'+str(constants.START_YEAR)+'_'+state # OPEN_20xx_<state_name>
    constants.make_dir_if_missing(constants.epic_dir+os.sep+state)

    # Create output directory for each state
    state_dir  = constants.out_dir+os.sep+state+os.sep
    constants.make_dir_if_missing(state_dir)

    # Reclass for each year
    idx = 0
    for yr in range_of_yrs:
        recl_raster = constants.shared_dir+constants.RECL+'_'+state+'_'+str(yr)

        if arcpy.Exists(recl_raster) and not(replace):      
            idx += 1      
        else:
            try:
                out_reclass = ReclassByASCIIFile(state_cdl_files[idx],constants.REMAP_FILE,"NODATA")        
                out_reclass.save(recl_raster)
                idx        += 1
            except:
                logging.info(arcpy.GetMessages())
        
        logging.info('\tReclassified...'+recl_raster)
        to_comb_rasters.append(recl_raster)

        # Extract open land acreage in the last year
        if (yr == constants.END_YEAR): 
            if arcpy.Exists(end_open_ras) and not(replace):
                pass
            else:
                where = "VALUE = "+str(constants.OPEN)
                try:
                    att_extract = ExtractByAttributes(recl_raster,where) 
                    att_extract.save(end_open_ras)     
                    
                    create_zonal_state(state,end_open_ras,constants.START_YEAR)               
                except:
                    logging.info(arcpy.GetMessages())
                logging.info('\tExtracted Open Lands...'+end_open_ras)
        elif(yr == constants.START_YEAR): # Extract open land acreage in the first year
            if arcpy.Exists(start_open_ras) and not(replace):
                pass
            else:
                where = "VALUE = "+str(constants.OPEN)
                try:
                    att_extract = ExtractByAttributes(recl_raster,where) 
                    att_extract.save(start_open_ras)        
                    
                    create_zonal_state(state,start_open_ras,constants.END_YEAR)                        
                except:
                    logging.info(arcpy.GetMessages())
                logging.info('\tExtracted Open Lands...'+start_open_ras)

    to_comb_rasters.append(state_lcc)
    
    # Combine all input rasters
    comb_raster = constants.shared_dir+os.sep+'comb_'+state+'_'+str(range_of_yrs[0])[2:]+'_'+str(range_of_yrs[len(range_of_yrs)-1])[2:]
      
    if arcpy.Exists(comb_raster) and not(replace):
        pass
    else:     
        try:   
            out_combine = Combine(to_comb_rasters)
            out_combine.save(comb_raster)
        except:
            logging.info(arcpy.GetMessages())
        
    logging.info('\tCombined...'+comb_raster)
    return comb_raster

###############################################################################
#
#
#
#
############################################################################### 
def create_state_ssurgo(state,replace):    
    state_lcc_dir  = constants.lcc_dir+state+os.sep
    
    state_ssurgo  = state_lcc_dir+state+'ssurgo'
    lu_ssurgo     = state_lcc_dir+state+'_lu_ssurgo'    
    out_state_sgo = state_lcc_dir+state+'_sgo_'+constants.METRIC.lower()
    
    # Join with LCC csv
    if arcpy.Exists(out_state_sgo) and not(replace):
        pass
    else:
        arcpy.BuildRasterAttributeTable_management(state_ssurgo, "Overwrite")

        try:
            if(constants.METRIC=='LCC'):
                arcpy.JoinField_management (state_ssurgo,"VALUE",constants.LCC_CR,"mukey","")
            else: # DI or PI            
                arcpy.JoinField_management (state_ssurgo,"VALUE",DI_PI_CR,"mukey","")                
        except:
            logging.info(arcpy.GetMessages())
            
        # Lookup to create new raster with new VALUE field
        # Execute Lookup
        lup_column = ''
        remap_file = ''
        
        if(constants.METRIC=='LCC'):
            lup_column = 'NICCDCD'
            remap_file = constants.SSURGO_REMAP_FILE
        elif(constants.METRIC=='PI'):
            lup_column = 'PI'
            remap_file = constants.PI_REMAP_FILE
        elif(constants.METRIC=='DI'):
            lup_column = 'DI'
            remap_file = constants.DI_REMAP_FILE
                        
        lu_tmp = Lookup(state_ssurgo,lup_column)        
        # Save the output 
        lu_tmp.save(lu_ssurgo)
        
        # Reclass raster to group LCC values into 3 classes: 
        # Productive, Moderate and Marginal
        out_reclass = ReclassByASCIIFile(lu_ssurgo,remap_file,"NODATA")        
        out_reclass.save(out_state_sgo)
    
    logging.info('\t SSURGO state '+state)
    return out_state_sgo

###############################################################################
#
#
#
#
###############################################################################    
def merge_csv_files(list_csv_files,fname):
    write_file = constants.out_dir+fname+'.csv'

    with open(write_file,'w+b') as append_file:
        need_headers = True
        for input_file in list_csv_files:
            input_file = input_file.replace("\\", "\\\\")
            with open(input_file,'r') as read_file:
                headers = read_file.readline()
                if need_headers:
                    # Write the headers only if we need them
                    append_file.write(headers)
                    need_headers = False
                # Now write the rest of the input file.
                for line in read_file:
                    append_file.write(line)
    logging.info('Appended CSV files')
    return write_file
    
###############################################################################
# 
#
#
#
###############################################################################       
def lu_change_analysis(state,df):
    names_lu_conversion = []
    non_region_csv_fl   = []
    matrix_names        = []
    for i in combinations_with_replacement(constants.LANDUSE, 2):
        # Do not include transition like CULT_CORN
        # or SOY_CULT etc. Only CULT_ 'Non cult' transitions
        # make sense
        if(i[0]=='CULT' and check_if_ag(constants.LANDUSE[i[1]])):
            pass
        elif(i[1]=='CULT' and check_if_ag(constants.LANDUSE[i[0]])):
            pass
        else:
            names_lu_conversion.append(i[0]+'_'+i[1])
            if(i[0] <> i[1]):            
                names_lu_conversion.append(i[1]+'_'+i[0])
                
        if(constants.LANDUSE[i[1]]==constants.WHEAT or constants.LANDUSE[i[1]]==constants.CORN or constants.LANDUSE[i[1]]==constants.SOY or constants.LANDUSE[i[1]]==constants.WATER or\
           constants.LANDUSE[i[0]]==constants.WHEAT or constants.LANDUSE[i[0]]==constants.CORN or constants.LANDUSE[i[0]]==constants.SOY or constants.LANDUSE[i[0]]==constants.WATER or\
           (i[0]=='CULT' and i[1]=='OTHER') or\
           (i[0]=='OTHER' and i[1]=='CULT')):
            pass
        else:
            matrix_names.append(i[0]+'_'+i[1])
            if(i[0] <> i[1]):            
                matrix_names.append(i[1]+'_'+i[0])
        
    # Add columns to df
    for i in names_lu_conversion:
        df[i] = numpy.random.randn(len(df['VALUE']))
        df[i] = 0.0
    
    # Iterate through df rows and compute land use conversion between the different LU classes
    name_init = 'RECL_'+state.upper()+'_'+str(constants.START_YEAR)
    name_finl = 'RECL_'+state.upper()+'_'+str(constants.END_YEAR)    
    
    # Iterate through names_lu_conversion and determine land use change area
    for index, row in df.iterrows():
        # Convert from LU to column name
        #col_name = lu_to_colname()

        init = constants.OPP_LU[row[name_init]]
        finl = constants.OPP_LU[row[name_finl]]        
        col_name = init+'_'+finl
        df.loc[index,col_name] = row['COUNT']
        
        if(init in constants.CULT and finl in constants.CULT):
            pass            
        elif(init in constants.CULT and finl not in constants.CULT):
            col_name = 'CULT'+'_'+finl
            df.loc[index,col_name] = row['COUNT']
        elif(init not in constants.CULT and finl in constants.CULT):
            col_name = init+'_'+'CULT'
            df.loc[index,col_name] = row['COUNT']
        else:
            pass
                    
    # Create new data frame
    #mat_df = pandas.DataFrame(columns=names_lu_conversion, index = numpy.arange(1))
    mat_df = pandas.DataFrame(columns=matrix_names, index = numpy.arange(1))
    
    # Output region to matrix 
    for reg in constants.REGION:                    
        for i in matrix_names:#names_lu_conversion:
            reg_df    = df[df['REGION']==reg]
            mat_df[i] = reg_df[i].sum()        
            output_as_matrix(mat_df,'matrix_'+reg+'_'+state+'_'+constants.TAG)
                        
    # Output entire state
    for i in matrix_names:#names_lu_conversion:
        mat_df[i] = df[i].sum()            
    output_as_matrix(mat_df,'matrix_'+state+'_'+constants.TAG)        
    

    # Use all columns except the ones with values that are not the same for the same VALUE 
    exclude_cols = names_lu_conversion[:]
    exclude_cols.append('REGION')
    exclude_cols.append('COUNT')
    exclude_cols.append('Rowid')
    
    cols = [col for col in df.columns if col not in exclude_cols]
    # Discard duplicate rows
    df2  = df[cols].drop_duplicates()
    # Aggregate some columns        
    cols_to_append = names_lu_conversion[:] 
    cols_to_append.append('COUNT')
    #gr = df.groupby('VALUE').aggregate({'COUNT':numpy.sum},as_index=False)
    #gr['VALUE'] = gr.index
    
    gr = df.groupby(['VALUE'],as_index=False)[cols_to_append].sum()   
    df2  = df2.merge(gr,how='left',on='VALUE')
    df2.to_csv(constants.out_dir+state+'_'+constants.TAG+'.csv') # Contains results with no region separation
    non_region_csv_fl.append(constants.out_dir+state+'_'+constants.TAG+'.csv')
    
    merge_csv_files(non_region_csv_fl,'NonRegion_'+constants.TAG)

def open_lands_conv(state):
    # Loop across all states  
    fl                = '' 
    list_csv_files    = []
    list_filt_ras     = [] 
    region_csv_files  = []
    state_cdl_files   = []
    range_of_yrs      = numpy.arange(constants.START_YEAR,constants.END_YEAR+1)
   
    for subdir, dir_list, files in os.walk(constants.cdl_dir):
            break   

    # Collect all CDL files for state within given year range   
    for yr in range_of_yrs:
        for position, item in enumerate(dir_list):
            if (str(yr) in item):
                cdl_file = glob.glob(constants.cdl_dir+os.sep+dir_list[position]+os.sep+state+os.sep+'*_'+state+'_*'+str(yr)+'*.tif')
                if cdl_file:                    
                    state_cdl_files.append(''.join(cdl_file))
                else:
                    logging.info(cdl_file + 'not found!')
                    sys.exit(0)

    # Set snap extent
    arcpy.env.snapRaster     = state_cdl_files[0]
    logging.info('\tSet snap extent')

    # 0. Create SSURGO file
    state_sgo     = create_state_ssurgo(state,True and constants.REPLACE)

    # 1. Combine CDL (START_YEAR ... END_YEAR) + SSURGO    
    comb_raster   = reclassify_and_combine(state,state_sgo,state_cdl_files,range_of_yrs,False)#True and constants.REPLACE)

    # 2. Add field indicating land-use conversion and corn/soy cropping
    out_csv       = identify_no_change_pixels(state,comb_raster,True and constants.REPLACE)

    # 5. Erase the PAD
    extract_comb  = erase_PAD(state,comb_raster,True and constants.REPLACE)
                
    # 4. Remove non LU change pixels from raster
    LU_change_ras = extract_LU_change(state,extract_comb,True and constants.REPLACE)        

    # 5. Extract by regional mask
    extract_mask  = extract_by_mask(state,LU_change_ras,'',True and constants.REPLACE)
    all_mask  = extract_by_mask(state,extract_comb,'al',True and constants.REPLACE)
                                
    reg_indx = 0
    state_csv_files = []
    state_filt_ras  = []
    to_merge_all    = [] 
    for ras in extract_mask:
        reg = constants.REGION[reg_indx]            
        reg_indx += 1
            
        # 5.5 Output csv corresponding to ras
        for r in all_mask:
            try:
                out_CR = constants.out_dir+os.sep+state+os.sep+'all_'+state+'_'+reg+'_cr'
                arcpy.CopyRows_management(out_csv,out_CR)        
                arcpy.BuildRasterAttributeTable_management(r,"Overwrite")
                arcpy.JoinField_management(r,"VALUE",out_CR,"VALUE","")
            except:
                logging.info(arcpy.GetMessages())
            
        all_reg_csv = output_raster_attribute_to_csv(reg,state,r,'all_',True and constants.REPLACE)
        # read in all_reg_csv into pandas dataframe, extract only CONVERSION < 0, output back into csv
        tmp_df = pandas.DataFrame.from_csv(all_reg_csv,index_col=False)
        tmp_df = tmp_df[tmp_df['CONVERSION']<0]
        tmp_df.to_csv(constants.out_dir+os.sep+state+os.sep+'all_unchanged_'+state+'_'+reg+'.csv')
        to_merge_all.append(constants.out_dir+os.sep+state+os.sep+'all_unchanged_'+state+'_'+reg+'.csv')
        # 6. Remove small pixels
        filtered_ras = filter_and_project_raster(reg,state,ras,False and constants.REPLACE)
                 
        # 7. Join back the csv
        join_csv(reg,state,filtered_ras,out_csv,True)
        list_filt_ras.append(filtered_ras)
        state_filt_ras.append(filtered_ras)
         
        # 8. Join back the csv
        out_csv_file = output_raster_attribute_to_csv(reg,state,filtered_ras,'',True and constants.REPLACE)
        state_csv_files.append(out_csv_file)
    
         
    # Get raster cell area
    try:
        ras_cell_size = int(arcpy.GetRasterProperties_management(filtered_ras, 'CELLSIZEX').getOutput(0))
        ras_area      = ras_cell_size*ras_cell_size*constants.M2_TO_HA # Assuming cell is a square
    except:
        logging.info(arcpy.GetMessages())

    # Merge state csv files
    # Each state csv file contains all the data but separated by region     
    state_csv = merge_csv_files(state_csv_files,'append_'+state+'_'+constants.TAG)#+'_'+date)
    region_csv_files.append(state_csv)
    df   = pandas.DataFrame.from_csv(state_csv,index_col=False)
    df['COUNT']   *= ras_area

    # Perform land use change analysis
    lu_change_analysis(state,df)        

    region_csv_files.extend(to_merge_all) # extending because to_merge_all is itself a list
    # Zonal state analysis for county specific totals
    if(constants.DO_MOSAIC):
        try:
            out_CR   = constants.out_dir+os.sep+'out_cr'
            merg_ras = state+"_merge_"+constants.METRIC
                
            # Combine all filtered rasters
            arcpy.MosaicToNewRaster_management(";".join(state_filt_ras),constants.out_dir,merg_ras,"","32_BIT_SIGNED","","1","LAST","FIRST")
            arcpy.BuildRasterAttributeTable_management(constants.out_dir+merg_ras, "Overwrite")
            logging.info('Mosaiced... '+constants.out_dir+merg_ras)
        except:
            logging.info(arcpy.GetMessages())   
            
        try:             
            # Perform lookup on COUNT column, since we want to perform zonal stat on area/count
            lu_tmp = Lookup(constants.out_dir+merg_ras,'COUNT')        
            lu_tmp.save(constants.out_dir+'lup_'+state+'_'+constants.METRIC)
        except:
            logging.info(arcpy.GetMessages())

            # Zonal stat
        try:
            in_zone_data = constants.base_dir+'Data\\GIS\\UScounties\\LakeStateCounty.shp'        
            out_zsat     = ZonalStatisticsAsTable(in_zone_data,'FIPS',constants.out_dir+'lup_'+state+'_'+constants.METRIC,constants.out_dir+state+'_zsat.dbf', "DATA", "SUM")              
            logging.info('Zonal stat as table... '+constants.out_dir+state+'_zsat.dbf')
        except:
            logging.info(arcpy.GetMessages())

        try:
            out_zonal_statistics = ZonalStatistics(in_zone_data,'FIPS',constants.out_dir+'lup_'+state+'_'+constants.METRIC,"SUM","DATA")
            out_zonal_statistics.save(constants.out_dir+state+'_zsat')         
            logging.info('Zonal stat... '+constants.out_dir+state+'_zsat')
        except:
            logging.info(arcpy.GetMessages())
                     
    fl = dbf_to_csv(constants.out_dir+state+'_zsat.dbf')
    return fl

###############################################################################
# main
#
#
#
###############################################################################   
if __name__ == "__main__":
    # Backup source code
    backup_source_code(constants.out_dir)

    # Convert LCC_CSV into copy rows file
    try:
        arcpy.CopyRows_management(constants.LCC_CSV,constants.LCC_CR,"")
        arcpy.CopyRows_management(constants.DI_PI_CSV,constants.DI_PI_CR,"")       
        logging.info('Copying rows '+constants.LCC_CSV)
    except:
        logging.info(arcpy.GetMessages())                

    pool = multiprocessing.Pool(constants.max_threads)
    list_files = pool.map(open_lands_conv,constants.list_st)
    pool.close()
    pool.join()

    if(constants.DO_MOSAIC):
        merge_csv_files(list_files,'Zonal_'+constants.TAG)    
    
    #merge_csv_files(region_csv_files,'Region_'+constants.TAG)    
    logging.info('Done!')
    
