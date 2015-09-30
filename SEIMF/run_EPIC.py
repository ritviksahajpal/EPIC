import constants, subprocess, logging, os, glob, shutil

def run_EPIC_store_output():
    # Change directory to where EPIC sims will take place
    cur_dir = os.getcwd()
    os.chdir(constants.opt_rundir)
    try:
        # Run EPIC
        with open(os.devnull, "w") as f:
            subprocess.call(constants.EPIC_EXE, stdout=f, stderr=f)
    except:
        logging.info('Error in running '+constants.EPIC_EXE)

    # Create output directory
    out_dir = constants.make_dir_if_missing(constants.opt_rundir + os.sep + 'output')

    # Loop over all EPIC output files
    for fl_type in constants.EPICOUT_FLS:
        fl_dir = constants.make_dir_if_missing(out_dir + os.sep + fl_type)
        for file_name in glob.iglob(os.path.join(constants.epic_dly, '*.'+fl_type)):
            print file_name
            shutil.move(file_name, fl_dir + os.sep + file_name)

    # Change directory back to original
    os.chdir(cur_dir)

if __name__ == '__main__':
    run_EPIC_store_output()