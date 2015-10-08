###############################################################################
# NARR_to_text.py
# email: ritvik@umd.edu, 24th March, 2015
#
# Convert downloaded data to text
###############################################################################
import constants, util, logging, os, subprocess, pdb, multiprocessing, sys
import numpy as np

###############################################################################
# process_NARR_to_text
# Convert NARR netcdf file into a flat text file and create EPIC daily
# weather station list file
###############################################################################
def process_NARR_to_text(cur_var):
    # -s select format for output
    # -C controls which variable is extracted
    # -H prints data to screen
    # -d controls hyperslap
    # -v specify name of variable
    ncks_get = 'ncks -s \'%f\' -C -H -d '    
    ncks_sub = 'ncks -d '

    # _U unpacking
    # -o force overwriting of existing file
    ncpdq_fn = 'ncpdq -U -O '
    var_name = constants.vars_to_get.get(cur_var)

    # Extract Lon and Lat boundaries
    logging.info('Extracting boundary by lon and lat')        
    latli,latui,lonli,lonui = util.get_boundary_region(constants.narr_dir+os.sep+cur_var+os.sep+cur_var+'.'+str(constants.START_YR)+'.nc')

    for year in range(constants.START_YR,constants.END_YR+1):
        inp_nc   = constants.narr_dir+os.sep+cur_var+os.sep+cur_var+'.'+str(year)+'.nc'       # Input netcdf
        unp_nc   = os.path.dirname(constants.out_dir)+os.sep+'Data'+os.sep+cur_var+os.sep+cur_var+'.'+str(year)+'.nc' # Unpacked netcdf

        # In netcdf file is missing, bail
        if not(os.path.isfile(inp_nc)):
            logging.info(inp_nc+' not present. Exiting!')
            sys.exit(0)

        # Create output directory by netcdf variable and by year
        util.make_dir_if_missing(os.path.dirname(constants.out_dir)+os.sep+'Data'+os.sep+cur_var+os.sep+str(year))
                
        if not(os.path.isfile(unp_nc)):
            # Subset netcdf file by lat and lon boundaries        
            logging.info('Subsetting '+var_name+' by lon and lat')        
            subst_str = subprocess.check_output((ncks_sub+' x,'+str(lonli)+','+str(lonui)+' -d y,'+str(latli)+','+str(latui)+' '+inp_nc +' '+unp_nc))
            # Unpack to convert netcdf into a readable format
            logging.info('Unpacking '+var_name+' variable for '+str(year))
            unpck_str = subprocess.check_output(ncpdq_fn+unp_nc+' '+unp_nc)
        else:
            logging.info('File exists: '+unp_nc)        

        # Create EPIC weather station list file
        wth_fl = constants.out_dir+os.sep+constants.EPIC_DLY
        mon_fl = constants.out_dir+os.sep+constants.EPIC_MON
        wxr_fl = constants.epic_dly+os.sep+constants.WXPMRUN

        if(year==constants.START_YR and (not(os.path.isfile(wth_fl)) or not(os.path.isfile(mon_fl)) or not(os.path.isfile(wxr_fl)))):
            logging.info('Creating EPIC weather station list file')
            # Create EPIC weather list file            
            epic_wth = open(wth_fl,'w')
            epic_mon = open(mon_fl,'w')
            wxrmrun  = open(wxr_fl,'w')

            # The first year NARR data file is used to extract longitude and latitude
            idx = 1
            for i in range(0,lonui-lonli):
                for j in range(0,latui-latli):
                    lon_str = subprocess.check_output(ncks_get+'x,'+str(i)+','+str(i)+' -d '+'y,'+str(j)+','+str(j)+' -v lon '+unp_nc).strip("\r\n\t '")
                    lat_str = subprocess.check_output(ncks_get+'x,'+str(i)+','+str(i)+' -d '+'y,'+str(j)+','+str(j)+' -v lat '+unp_nc).strip("\r\n\t '")
                    epic_wth.write('%5s    "%10s"    %5.3f    %5.3f\n' % (idx,'daily//'+str(j)+'_'+str(i)+'.txt',np.float(lat_str),np.float(lon_str)))
                    epic_mon.write('%5s    "%10s"    %5.3f    %5.3f\n' % (idx,'monthly//'+str(j)+'_'+str(i)+'.txt',np.float(lat_str),np.float(lon_str)))
                    if i==(lonui-lonli-1) and j==(latui-latli-1):
                        wxrmrun.write(str(j)+'_'+str(i))
                    else:
                        wxrmrun.write(str(j)+'_'+str(i)+'\n')
                    idx += 1

            epic_wth.close()
            epic_mon.close()
            wxrmrun.close()

        # Extract all data from variable for given co-ord (data is a time series)
        logging.info('Extracting '+var_name+' variable for '+str(year))
        for i in range(0,lonui-lonli):
            for j in range(0,latui-latli):
                if(not(os.path.isfile(os.path.dirname(constants.out_dir)+os.sep+'Data'+os.sep+cur_var+os.sep+str(year)+os.sep+str(j)+'_'+str(i)+'.txt'))):
                    exec_str = ncks_get+\
                                'x,'+str(i)+','+str(i)+' -d '+'y,'+str(j)+','+str(j)+\
                                ' -v '+var_name+' '+unp_nc+\
                                ' > ' + os.path.dirname(constants.out_dir)+os.sep+'Data'+os.sep+cur_var+os.sep+str(year)+os.sep+str(j)+'_'+str(i)+'.txt'
                    os.system(exec_str)
                else:
                    logging.info('File exists: '+os.path.dirname(constants.out_dir)+os.sep+'Data'+os.sep+cur_var+os.sep+str(year)+os.sep+str(j)+'_'+str(i)+'.txt')

###############################################################################
# parallelize_NARR_to_text
# Iterate/Parallelize NARR netcdf conversion to text
#
###############################################################################
def parallelize_NARR_to_text():
    pkg_num = 0
    threads = []
    total_runs = len(constants.vars_to_get) # Find total number of runs based on number of NARR elements to extract    

    if(constants.DO_PARALLEL):
        pool = multiprocessing.Pool(constants.max_threads)
        pool.map(process_NARR_to_text, constants.vars_to_get.keys())
        pool.close()
        pool.join()
    else:
        for pkg_num,c_var in enumerate(constants.vars_to_get):
            process_NARR_to_text(c_var)
    logging.info('Done NARR_to_text!')

if __name__ == '__main__':
    parallelize_NARR_to_text()