import constants, logging, sys, netCDF4, os, errno
import numpy as np

###############################################################################
#
#
#
###############################################################################
def make_dir_if_missing(d):
    try:
        os.makedirs(d)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

###############################################################################
# log_constants
#
#
###############################################################################
def log_constants():
    logging.info('*****************************************************************')     
    logging.info('NARR variables: '+','.join(constants.vars_to_get.keys()))
    logging.info('Start year: '+str(constants.START_YR))
    logging.info('End year: '+str(constants.END_YR))
    logging.info('Lat boundary: '+str(constants.LAT_BOUNDS[0])+' '+str(constants.LAT_BOUNDS[1]))
    logging.info('Lon boundary: '+str(constants.LON_BOUNDS[0])+' '+str(constants.LON_BOUNDS[1]))
    logging.info('Input dir: '+constants.narr_dir)
    logging.info('Output dir: '+constants.out_dir)
    logging.info('DO_PARALLEL: '+str(constants.DO_PARALLEL))
    logging.info('*****************************************************************') 

###############################################################################
# get_closest_ij
# From http://nbviewer.ipython.org/github/Unidata/netcdf4-python/blob/master/examples/reading_netCDF.ipynb
# A function to find the index of the point closest pt (in squared distance)
# to give lat/lon value.
###############################################################################
def get_closest_ij(lats,lons,lat_pt,lon_pt):
    # find squared distance of every point on grid
    dist_sq = (lats-lat_pt)**2 + (lons-lon_pt)**2  

    # 1D index of minimum dist_sq element
    min_index_flattened = dist_sq.argmin()    

    # Get 2D index for latvals and lonvals arrays from 1D index
    return np.unravel_index(min_index_flattened, lats.shape)

###############################################################################
# get_boundary_region
# Convert X and Y coords to actual lat lon
#
###############################################################################
def get_boundary_region(nc_file):
    try:
        nc_f = netCDF4.Dataset(nc_file)
    except:
        logging.info(nc_file+' not present. Exiting!')
        sys.exit(0)

    lats = nc_f.variables['lat'][:] 
    lons = nc_f.variables['lon'][:]

    # Latitude range
    latli,lon = get_closest_ij(lats,lons,constants.LAT_BOUNDS[0],constants.LON_BOUNDS[0])
    latui,lon = get_closest_ij(lats,lons,constants.LAT_BOUNDS[1],constants.LON_BOUNDS[0])

    # Longitude range
    lat,lonli = get_closest_ij(lats,lons,constants.LAT_BOUNDS[0],constants.LON_BOUNDS[0])
    lat,lonui = get_closest_ij(lats,lons,constants.LAT_BOUNDS[0],constants.LON_BOUNDS[1])

    logging.info('Boundary: '+str(latli)+' ' +str(latui)+' '+str(lonli)+' '+str(lonui))
    return latli,latui,lonli,lonui

###############################################################################
# chunks
# Divide list into 'n' sized chunks or smaller. Compute min or max on these chunks
#
###############################################################################
def chunks(lis, n, do_min):
    n = max(1, n)

    if do_min:
        return [min(lis[i:i + n]) for i in range(0, len(lis), n)]
    else:
        return [max(lis[i:i + n]) for i in range(0, len(lis), n)]

###############################################################################
# chunk_file
# 
#
###############################################################################
def chunk_file(l, n):
    #Generator to yield n sized chunks from l
    for i in xrange(0, len(l), n):
        yield l[i: i + n]