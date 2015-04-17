###############################################################################
# wget_NARR.py
# email: ritvik@umd.edu, 24th March, 2015
#
# Download NARR data based on user specified region/site, variables and years
###############################################################################
import constants, logging, os, wget, util, multiprocessing

###############################################################################
# download_NARR
# Download NARR file corresponding to variable (cur_var) and years
#
###############################################################################
def download_NARR(cur_var):
    for year in range(constants.START_YR,constants.END_YR+1):        
        util.make_dir_if_missing(constants.data_dir+cur_var)
 
        if(not os.path.exists(constants.data_dir+cur_var+os.sep+cur_var+'.'+str(year)+'.nc')):
            if(cur_var == "air.2m"):
                url    = constants.TEMP_CMD+cur_var+'.'+str(year)+'.nc'
            else:
                url    = constants.BASE_CMD+cur_var+'.'+str(year)+'.nc'
            
            # Download
            out_nc = constants.data_dir+cur_var+os.sep+cur_var+'.'+str(year)+'.nc'
            wget.download(url,out=out_nc,bar=False)
            logging.info('Downloaded... '+cur_var+'.'+str(year)+'.nc')
        else:
            logging.info('File exists '+constants.data_dir+cur_var+os.sep+cur_var+'.'+str(year)+'.nc')        

###############################################################################
# parallelize_download_NARR
# Iterate/Parallelize NARR download
#
###############################################################################
def parallelize_download_NARR():
    
    pkg_num = 0
    total_runs = len(constants.vars_to_get) # Find total number of runs based on number of NARR elements to extract
    threads = []

    if(constants.DO_PARALLEL):
        pool = multiprocessing.Pool(constants.max_threads)
        pool.map(download_NARR, constants.vars_to_get.keys())
        pool.close()
        pool.join()
    else:
        for pkg_num,c_var in enumerate(constants.vars_to_get):
            download_NARR(c_var)
    logging.info('Done wget_NARR!')