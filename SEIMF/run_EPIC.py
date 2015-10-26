import constants, subprocess, logging, os, glob, shutil, pdb, time

def copytree(src, dst, symlinks=False, ignore=None):
    """
    From stackoverflow
    :param src:
    :param dst:
    :param symlinks:
    :param ignore:
    :return:
    """
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def copy_EPIC_mgt_files():
    # Copy over mgt directory (containing .ops files) to the EPIC input files directory
    try:
        constants.make_dir_if_missing(constants.mgt_dir + os.sep + constants.MGT_TAG)
        copytree(constants.epic_dir + os.sep + 'Data' + os.sep + constants.MGT_TAG, constants.mgt_dir + os.sep + constants.MGT_TAG)
    except:
        logging.info('Cannot copy over management directory to EPIC input files directory')

def copy_EPIC_dat_files(epic_folder):
    # Copy EPIC dat files: EPICRUN.dat, iewedlst.dat, iewealst.dat, ieSllist and ieSitelist
    try:
        copytree(constants.sims_dir + os.sep, epic_folder)
    except:
        logging.info('Cannot copy EPIC dat files')

def copy_EPIC_input_folders():
    """
    :return:
    """
    # Change directory to where EPIC sims will take place
    time_stamp = time.strftime('%m_%d_%Y_%Hh_%Mm')
    epic_run_dir = constants.run_dir + '_' + time_stamp + os.sep
    constants.make_dir_if_missing(epic_run_dir)

    try:
        # Copy all files from constants.sims_dir to constants.run_dir
        copytree(constants.temp_dir + os.sep, epic_run_dir)
        # Copy over .DAT files produced through NARR, SSURGO and seimf scripts
        copytree(constants.epic_dir + os.sep + 'Data' + os.sep + constants.MGT_TAG, epic_run_dir)
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

    return time_stamp, epic_run_dir

def store_EPIC_Output(dir_path='', epic_run_dir=''):
    """
    :param time_stamp:
    :param epic_run_dir:
    :return:
    """
    # Create output directory
    out_dir = constants.make_dir_if_missing(constants.epic_dir + os.sep + 'output' + os.sep + dir_path)

    # Loop over all EPIC output files and move them to separate subfolders in the output directory
    for fl_type in constants.EPICOUT_FLS:
        fl_dir = constants.make_dir_if_missing(out_dir + os.sep + fl_type)
        for file_name in glob.iglob(os.path.join(epic_run_dir, '*.'+fl_type)):
            if os.path.basename(file_name)[:-4] <> 'xxxxx':
                shutil.move(file_name, fl_dir + os.sep + os.path.basename(file_name))

def run_EPIC_store_output():
    """
    :return:
    """
    tstmp = ''
    erun_dir = ''
    cur_dir = os.getcwd()

    # Copy the management directory containing .ops files
    if not constants.DO_FOLDER:
        copy_EPIC_mgt_files()
        tstmp, erun_dir = copy_EPIC_input_folders()
        # Copy EPIC.dat files
        copy_EPIC_dat_files(erun_dir)

    # Run EPIC model
    try:
        if constants.DO_FOLDER:
            os.chdir(constants.FOLDER_PATH)
        with open(os.devnull, "w") as f:
            subprocess.call(constants.EPIC_EXE, stdout=f, stderr=f)
    except:
        logging.info('Error in running ' + constants.EPIC_EXE)

    if not constants.DO_FOLDER:
        store_EPIC_Output(dir_path=constants.OUT_TAG + '_' + tstmp, epic_run_dir=erun_dir)
    else:
        store_EPIC_Output(dir_path=constants.FOLDER_PATH, epic_run_dir=erun_dir)

    # Change directory back to original
    os.chdir(cur_dir)

if __name__ == '__main__':
    run_EPIC_store_output()