import constants, glob, os, pdb, shutil, subprocess, logging

def create_monthly():
    try:
        shutil.copyfile(constants.meta_dir+os.sep+constants.WXPM_EXE,constants.epic_dly+constants.WXPM_EXE)
    except:
        logging.info('Error in copying '+constants.meta_dir+os.sep+constants.WXPM_EXE)
    
    for filename in glob.iglob(os.path.join(constants.epic_dly, '*.txt')):
        shutil.copyfile(filename,filename[:-4]+'.PRN')
    
    # Run WXPM3020
    cur_dir = os.getcwd()
    os.chdir(constants.epic_dly)
    try:
        with open(os.devnull, "w") as f:
            subprocess.call(constants.WXPM_EXE,stdout=f,stderr=f)
    except:
        logging.info('Error in running '+constants.WXPM_EXE)
    os.chdir(cur_dir)

    # Copy daily files to the monthly folder and rename to *.PRN    
    for filename in glob.iglob(os.path.join(constants.epic_dly, '*.INP')):
        shutil.move(filename, constants.epic_mon+os.path.basename(filename[:-4])+'.txt')

    # Delete all .OUT and .PRN files
    for filename in glob.iglob(os.path.join(constants.epic_dly, '*.OUT')):
        os.remove(filename)

    for filename in glob.iglob(os.path.join(constants.epic_dly, '*.PRN')):
        os.remove(filename)

    logging.info('Done creating monthly files')

if __name__ == '__main__':
    create_monthly()
