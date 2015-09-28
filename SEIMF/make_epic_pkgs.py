import sys, os, shutil, logging, subprocess, pdb, multiprocessing, pexpect, time, glob, constants

#######################################################################
# USER SPECIFIED PARAMETERS
# The following parameters are user specified and might need to be changed
# outFileName:   Name of file containing a list of failed simulations
#######################################################################
# Output file where the messages from this script are kept
outFileName      = os.getcwd() + os.sep + 'Output_AutomateScript.txt'
# Log everything, and send it to stderr. (http://docs.python.org/library/logging.html)
# Logging levels are DEBUG, INFO, WARNING, ERROR, and CRITICAL
#logging.basicConfig(filename = outFileName, level = logging.INFO, filemode = 'w')
# terminatorStr denotes 'XXXX' to demarcate EPIC runs
terminatorStr = 'XXXX'

## "run_pkgs_directory is the directory where the Run programs and data are located."
## opt_testdb will return false if not on command line
## opt_updatedb will return true if old records are to be replaced by the updated records

logging.info ('opt_rundir = %s', constants.opt_rundir)
logging.info ('opt_epicrun = %s', constants.opt_epicrun)
logging.info ('opt_tag = %s', constants.opt_tag)
logging.info ('opt_numpkgs = %d', constants.opt_numpkgs)
logging.info ('opt_outdir = %s', constants.opt_outdir)

# Outline:
# Read EPICRUN all lines into memory
# Do a little sanity checking (number of lines is greater than number of packages
# Determine number of lines to be copied into each package by dividing number of lines by opt_numpkgs
# For number of packages
#    Make directory in opt_outdir using opt_tag and current index
#    Recursively copy opt_rundir into created folder
#    Create EPICRUN.dat in created folder with its portion of opt_epicrun
#    Tar/GZIP the folder into a single, compressed file using opt_tag and current index (don't do because won't work on Windows)
# Need to add verification of values/error checking.  See David's os.access tests at bottom

## Read EPICRUN
filespec = opt_epicrun
epicrun = open (filespec, 'r')

epicruns = epicrun.readlines()
epicrunsnum = len (epicruns)
logger.info ('Number of runs is = %d', epicrunsnum)
epicrun.close()

if epicrunsnum < opt_numpkgs:
    raise EOFError ("EPICRUN contains too few runs for requested number of packages.")

epicrunsperpackage = epicrunsnum / opt_numpkgs  # integer division
epicrunsextraperpackage = epicrunsnum % opt_numpkgs  # any remainder, add an extra row to the first epicrunsextraperpackage number of packages
logger.info ('There will be %d runs per package with an extra run in the first %d packages', epicrunsperpackage, epicrunsextraperpackage)

currentRunNum = 0  # index of current row in epicruns
for pkgnum in range(opt_numpkgs):
    print "Creating package ", pkgnum
    logger.info ("Creating package %d", pkgnum)
    
    # Destination directory will be created by copytree()
    newPkgDir = opt_outdir + os.sep + opt_tag + str(pkgnum)
    logger.debug ('Destination directory for package is = %s', newPkgDir)

    # Recursively copy from Run template to new directory
    shutil.copytree(opt_rundir, newPkgDir,symlinks=True)
    
    # Create new EPICRUN.dat in package folder
    epicnewfilespec = newPkgDir + os.sep + "EPICRUN.DAT"
    epicnewfile = open(epicnewfilespec, 'w')
    logger.debug ('New EPICRUN file is %s', epicnewfilespec)
    
    rowsToWrite = epicrunsperpackage
    if pkgnum < epicrunsextraperpackage:  # extra row in first set of packages
    	rowsToWrite += 1
    	
    for rownum in range(rowsToWrite):
        epicnewfile.write(epicruns[currentRunNum])
        logger.debug ('Writing row = %d', currentRunNum)
        currentRunNum += 1
        
    epicnewfile.close()

# Find the number of runs, and the index of the last run in the EPIC file
def numRunsinEPICRUNDAT(pkgDir):
	fEPIC        = open(pkgDir+'EPICRUN.DAT', 'r')
	# Number of simulations to be run (from EPICRUN.DAT)
	numRuns      = 0
	# Index of the last simulation, so that we know when we are done
	lastRunIndex = 0

	for line in fEPIC:
		numRuns      = numRuns + 1
		lastRunIndex = line.split()[0]

	fEPIC.close()
	return numRuns, lastRunIndex

# Read the EPIC output file to find the EPIC simulation number where the run failed
# Also, return the number of lines in the EPICRUN.dat file occuring before the failed EPIC
# run. This is done so that we can modify the EPICRUN.dat file to start after the failed
# EPIC run
def FindCurrentEPICRun(fName):
	#     RUN#=     2006  SIT#=        2  WP1#=        3  SOL#=      906  OPS#=        6
	# Find the current EPIC run number by reading output.txt
	fOutput           = open(fName, 'r')
	simIndex          = 0
	numLinesBeforeSim = 0

	for line in fOutput:
                # The if statement below skips over empty lines
		if len(line) > 3:
			isRUN             = line.split()[0]

			if (isRUN  == 'RUN='):
				simIndex = line.split()[1]
				numLinesBeforeSim = numLinesBeforeSim + 1	
	fOutput.close()	
	return simIndex, numLinesBeforeSim

# Modify the EPICRUN.DAT file when an EPIC run fails.
# The list of all runs (upto and including the failed run)
# are moved to the end of the file so that EPIC.exe can continue 
# executing the remaining files
def modifyEPICFile(curRunLines,pkgDir):
	# Modify EPICRUN.DAT
	fEPICRead = open(pkgDir+'EPICRUN.DAT', 'r')
	epicData = fEPICRead.readlines()
	fEPICRead.close()
	# Cut the epicData from the start to curRunLines(both inclusive),
	# and move them at the end of the file after appending a 'XXXX' to
	# demarcate them
	cutEPICData = epicData[0: curRunLines]
	del epicData[0: curRunLines]

	# Append 'XXXX' at the end of EPICRUN.dat
	epicData.append(terminatorStr+'\n')
	# Append the cutEPICData at the end of EPICRUN.dat
	for i in range(0, len(cutEPICData)):
		epicData.append(cutEPICData[i])
	
	# Write the epicData structure to EPICRUN.DAT
	fEPICWrite = open(pkgDir+'EPICRUN.DAT','w')
	for line in epicData:	
		fEPICWrite.write(line)	
	fEPICWrite.close()

def runEPICSimulations(pkgDir):	
	print 'Running ' + str(pkgDir) + ' ...'
    	# Get the current directory
    	curDir = os.getcwd()
    	os.chdir(pkgDir)
	# Find the number of simulations and the index of the last simulation in the EPICRUN.dat file
	numEPICRuns, lastEPICRunIndex = numRunsinEPICRUNDAT(pkgDir)
	# Start executing EPIC simulation
	EPICParams = '.' + os.sep + ' '
	EPICCmd = '.' + os.sep + 'epic0810v5.release.pgi'
 
	child = pexpect.spawn(EPICCmd, [EPICParams])
	fout = file(pkgDir + 'output.txt', 'w')
	child.logfile = fout
	didEPICFail = child.expect(['FORTRAN PAUSE: ','ierror', terminatorStr, pexpect.EOF], timeout=None)
	DONE = False
	while(not DONE):
                # didEPICFail == 0 means that FORTRAN PAUSE was encountered. didEPICFail == 1 means that ierror was encountered
		if didEPICFail == 0 or didEPICFail == 1:
			# EPIC has failed, find out which simulation number it crashed on
			failedRun, successfulRuns = FindCurrentEPICRun(pkgDir+'output.txt')
			if int(failedRun) == int(lastEPICRunIndex):
				logging.info('Finished all ' + str(lastEPICRunIndex) + ' runs')
				DONE = True
			else:	
				logging.info('Simulation: ' + str(failedRun) + ' failed')
				modifyEPICFile(successfulRuns,pkgDir)

				# Restart EPIC simulation
				# Send a Ctrl-D signal to the child to terminate it
				child.sendcontrol('d')		
				child.close()

				# 
				child = pexpect.spawn(EPICCmd, [EPICParams])
				child.logfile = fout
				didEPICFail = child.expect(['FORTRAN PAUSE: ','ierror', terminatorStr, pexpect.EOF], timeout=None)
		else:
			logging.info('Finished all ' + str(lastEPICRunIndex) + ' runs')
			DONE = True

	fout.close()
	child.close()
	os.chdir(curDir)

if __name__ == '__main__':
    pkgnum = 0	
    numProcessors = multiprocessing.cpu_count() - 1
    threads = []

    while pkgnum < opt_numpkgs or len(threads):
        newPkgDir = opt_outdir + os.sep + opt_tag + str(pkgnum) + os.sep
        if(len(threads) < numProcessors and pkgnum < opt_numpkgs):
		pkgnum = pkgnum + 1
		t = multiprocessing.Process(target=runEPICSimulations,args=[newPkgDir])
                t.start()
                threads.append(t)
        else:
              for thread in threads:
                  if not thread.is_alive():
                      threads.remove(thread)	


# Find the number of runs that failed by counting the number of .ACY files in all the folders,
# and dividing them by the total number of lines in the EPICRUN.DAT file
numACYFiles = 0
lstSubdirsHighFailed = []

for parent_dir, dir_list, dir_files in os.walk(opt_outdir):
    break

for i in range(len(dir_list)):
    path = opt_outdir + os.sep+dir_list[i]
    numACYFiles_in_Subdir = 0
    for infile in glob.glob( os.path.join(path, '*.ACY') ):
        numACYFiles_in_Subdir = numACYFiles_in_Subdir + 1
	numACYFiles = numACYFiles + 1

    epicrun_in_subdir = open (path+os.sep+'EPICRUN.DAT', 'r')
    epicruns_in_subdir = epicrun_in_subdir.readlines()
    epicrunsnum_in_subdir = len (epicruns_in_subdir)
    epicrun_in_subdir.close()
    if (numACYFiles_in_Subdir/epicrunsnum_in_subdir) < 0.05:
	lstSubdirsHighFailed.append(dir_list[i])

logger.info ('Total number of .ACY files: ' + str(numACYFiles))
logger.info ('Total number of lines in EPICRUN.DAT: ' + str(epicrunsnum))
logger.info ('Percentage of failed runs: ' + str(100.0 - float(numACYFiles)*100.0/float(epicrunsnum)))
logger.info ('List of folders with more than 5 percent failed runs: ')

print 'Total number of .ACY files: ' + str(numACYFiles)
print 'Total number of lines in EPICRUN.DAT: ' + str(epicrunsnum)
print 'Percentage of failed runs: ' + str(100.0 - float(numACYFiles)*100.0/float(epicrunsnum))
print 'List of folders with > 5% failed runs: '
for i in range(len(lstSubdirsHighFailed)):
	logger.info (lstSubdirsHighFailed[i]+ ' ')
	print lstSubdirsHighFailed[i]
"""
This is code that checks for directory and file existence.

for result_dir in (FAILURE_DIR, SUCCESS_DIR):
    target_dir = epic_files_dir + os.sep + result_dir
    if not os.access (target_dir, os.F_OK):
        os.mkdir (target_dir)
        if not os.access (target_dir, os.F_OK):
            logger.critical ('Unable to create result directory: "%s"!', target_dir)
            sys.exit (-3)
    if not os.access (target_dir, os.W_OK):
        os.chmod (target_dir, 0777)
        if not os.access (target_dir, os.W_OK):
            logger.critical ('Unable to write to result directory: "%s"!', target_dir)
            sys.exit (-3)

    for type_dir in output_file_types.keys ():
        target_dir = epic_files_dir + os.sep + result_dir + os.sep + type_dir
        if not os.access (target_dir, os.F_OK):
            os.mkdir (target_dir)
            if not os.access (target_dir, os.F_OK):
                logger.critical ('Unable to create result directory: "%s"!', target_dir)
                sys.exit (-3)
        if not os.access (target_dir, os.W_OK):
            os.chmod (target_dir, 0777)
            if not os.access (target_dir, os.W_OK):
                logger.critical ('Unable to write to result directory: "%s"!', target_dir)
                sys.exit (-3)
"""
