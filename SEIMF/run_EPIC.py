import constants, subprocess, logging, os, glob, shutil, pdb, time

def run_EPIC_store_output():
    # Change directory to where EPIC sims will take place
    cur_dir = os.getcwd()
    os.chdir(constants.sims_dir)

    # Create symlinks to all folders in the management
    sub_dirs = os.listdir(constants.mgt_dir)

    for dir in sub_dirs:
        link = constants.sims_dir + os.sep + dir + os.sep
        trgt = constants.mgt_dir + os.sep + dir + os.sep

        # Windows
        if os.name == 'nt':
            subprocess.call('mklink /J "%s" "%s"' % (link, trgt), shell=True)

    try:
        # Run EPIC
        with open(os.devnull, "w") as f:
            subprocess.call(constants.EPIC_EXE, stdout=f, stderr=f)
    except:
        logging.info('Error in running '+constants.EPIC_EXE)

    # Create output directory
    out_dir = constants.make_dir_if_missing(constants.epic_dir + os.sep + 'output' + os.sep +
                                            time.strftime('%m_%d_%Y_%Hh_%Mm'))

    # Loop over all EPIC output files and move them to separate subfolders in the output directory
    for fl_type in constants.EPICOUT_FLS:
        fl_dir = constants.make_dir_if_missing(out_dir + os.sep + fl_type)
        for file_name in glob.iglob(os.path.join(constants.sims_dir, '*.'+fl_type)):
            shutil.move(file_name, fl_dir + os.sep + os.path.basename(file_name))

    # Change directory back to original
    os.chdir(cur_dir)

if __name__ == '__main__':
    run_EPIC_store_output()