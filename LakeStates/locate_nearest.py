import os, pdb
import constants_locate_nearest as constants
from geopy.distance import great_circle

def get_nearest_site():
    min_sit_wth = constants.MAX
    closest_loc = constants.site_lat_lon
    closest_sit = ''

    # Read in daily EPIC weather data file
    wth_fl  = open(constants.epic_dir+os.sep+constants.EPIC_DLY,'r')

    for wrow in wth_fl: #     1       0_0.txt    41.415    -97.932
        split_wrow  = wrow.split()
        lat_lon_wth = [float(split_wrow[2]), float(split_wrow[3])]
        dist        = great_circle(constants.site_lat_lon, lat_lon_wth).miles

        if dist < min_sit_wth:
            min_sit_wth = dist
            closest_sit = split_wrow[1]
            closest_loc = lat_lon_wth

    print 'Closest site to '+str(constants.site_lat_lon)+' is '+str(closest_loc)
    print 'EPIC weather file is: '+str(closest_sit)+' and distance is '+'{:.2f}'.format(min_sit_wth)+' miles.'

if __name__ == '__main__':
    get_nearest_site()
