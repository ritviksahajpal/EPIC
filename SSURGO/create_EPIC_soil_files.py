###############################################################################
# create_EPIC_soil_files.py
# email: ritvik@umd.edu, 10th April, 2015
#
#
#
###############################################################################
import os, pdb, merge_ssurgo_rasters, SSURGO_to_csv

if __name__ == '__main__':
    # Create EPIC soil text files
    df = SSURGO_to_csv.SSURGO_to_csv()
    SSURGO_to_csv.csv_to_EPIC(df)

    # Create SSURGO soil rasters
    merge_ssurgo_rasters.run_merge_ssurgo_rasters()
