###############################################################################
# create_EPIC_weather_files.py
# email: ritvik@umd.edu, 24th March, 2015
#
# 1. Download NARR data based on user specified region/site, variables and years
# 2. Convert downloaded data to text and then EPIC compatible weather files
###############################################################################
import wget_NARR,NARR_to_text,NARR_to_EPIC,create_EPIC_monthly,constants,util,pdb,logging

if __name__ == '__main__':
    # Store constants in log file
    util.log_constants()
    
    # Download NARR files
    wget_NARR.parallelize_download_NARR()
    # Convert NARR netcdf file into text files
    NARR_to_text.parallelize_NARR_to_text()
    # Convert text files into EPIC files
    NARR_to_EPIC.parallelize_NARR_to_EPIC()
    # Create EPIC monthly files
    create_EPIC_monthly.create_monthly()
