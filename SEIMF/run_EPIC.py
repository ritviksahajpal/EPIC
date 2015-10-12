import constants, subprocess, logging, os, glob, shutil, pdb, time

def run_EPIC_store_output():
    # Change directory to where EPIC sims will take place
    cur_dir = os.getcwd()
    time_stamp = time.strftime('%m_%d_%Y_%Hh_%Mm')
    epic_run_dir = constants.run_dir + '_' + time_stamp + os.sep

    # Copy all files from constants.sims_dir to constants.run_dir
    try:
        shutil.copytree(constants.sims_dir + os.sep, epic_run_dir)
    except:
        logging.info('Error in copying files to ' + constants.run_dir)
    os.chdir(epic_run_dir)

    # Create symlinks to all folders in the management
    sub_dirs = os.listdir(constants.mgt_dir)

    for dir in sub_dirs:
        link = epic_run_dir + os.sep + dir + os.sep # Specifies the name of the symbolic link that is being created.
        trgt = constants.mgt_dir + os.sep + dir + os.sep  # Specifies the path (relative or absolute) that the new symbolic link refers to.

        # Windows
        if os.name == 'nt':
            subprocess.call('mklink /J "%s" "%s"' % (link, trgt), shell=True)

    # Run EPIC model
    try:
        with open(os.devnull, "w") as f:
            subprocess.call(constants.EPIC_EXE, stdout=f, stderr=f)
    except:
        logging.info('Error in running '+constants.EPIC_EXE)

    # Create output directory
    out_dir = constants.make_dir_if_missing(constants.epic_dir + os.sep + 'output' + os.sep + time_stamp)

    # Loop over all EPIC output files and move them to separate subfolders in the output directory
    for fl_type in constants.EPICOUT_FLS:
        fl_dir = constants.make_dir_if_missing(out_dir + os.sep + fl_type)
        for file_name in glob.iglob(os.path.join(epic_run_dir, '*.'+fl_type)):
            if os.path.basename(file_name)[:-4] <> 'xxxxx':
                shutil.move(file_name, fl_dir + os.sep + os.path.basename(file_name))

    # Change directory back to original
    os.chdir(cur_dir)

if __name__ == '__main__':
    run_EPIC_store_output()