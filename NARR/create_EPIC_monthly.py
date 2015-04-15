import constants, glob, os, pdb, shutil, subprocess, logging

def create_monthly():
    shutil.copyfile(constants.base_dir+os.sep+'Meta'+os.sep+constants.WXPM_EXE,constants.epic_dly+constants.WXPM_EXE)
    
    for filename in glob.iglob(os.path.join(constants.epic_dly, '*.txt')):
        shutil.copyfile(filename,filename[:-4]+'.PRN')
    
    # Run WXPM3020
    cur_dir = os.getcwd()
    os.chdir(constants.epic_dly)
    try:
        subprocess.call(constants.WXPM_EXE,shell=True)
    except:
        logging.info('\n')
    os.chdir(cur_dir)

    # Copy daily files to the monthly folder and rename to *.PRN    
    for filename in glob.iglob(os.path.join(constants.epic_dly, '*.INP')):
        shutil.move(filename, constants.epic_mon+os.path.basename(filename[:-4])+'.txt')

    # Delete all .OUT and .PRN files
    for filename in glob.iglob(os.path.join(constants.epic_dly, '*.OUT')):
        os.remove(filename)

    for filename in glob.iglob(os.path.join(constants.epic_dly, '*.PRN')):
        os.remove(filename)

if __name__ == '__main__':
    create_monthly()
