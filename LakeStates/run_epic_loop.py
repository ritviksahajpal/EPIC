import os, pdb, shutil, subprocess
import extract_epic_output

EPIC_EXE = 'epic1102.exe'
base_dir = 'C:\\Users\\ritvik\\Documents\\PhD\\Projects\\EPIC\\Cedar_Creek - Copy\\'
soil_fl  = '395974.sol'

def make_copy(fl):
    try:
        shutil.copyfile(fl,os.path.splitext(fl)[0]+'_orig'+os.path.splitext(fl)[1])
    except:
        print 'Error in copying '

def revert_orig(fl):
    try:
        shutil.copyfile(os.path.splitext(fl)[0]+'_orig'+os.path.splitext(fl)[1],fl)
    except:
        print 'Error in copying '

def run_epic():
    cur_dir = os.getcwd()
    os.chdir(base_dir)

    try:
        with open(os.devnull, "w") as f:
            subprocess.call(EPIC_EXE,stdout=f,stderr=f)
    except:
        print 'Error in running EPIC'

    os.chdir(cur_dir)

