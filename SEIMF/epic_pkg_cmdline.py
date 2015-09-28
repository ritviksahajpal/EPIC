import sys,logging
import getopt  # command line parsing

## Command Line Options Processing
## opt_files_dir will return None if not on command line - alternate directory for import
## opt_testdb will return false if not on command line - used by Jeff to test db objects

def usage():
    print "Required parameters: "
    print "  -r or --rundir= <run_pkgs_directory> "
    print "  -f or --epicrun= <EPICRUN.dat> "
    print "  -t or --tag= <tagname> "
    print "  -n or --numpkgs= <number_of_packages>"
    print "  -o or --outdir= <pkg_build_folder>"
    print "rundir_directory is the directory where the Run programs and data are located."
    print "EPICRUN.dat is the directory and file name for the runs to be split.  Usually EPICRUN.dat"
    print "tagname is a descriptive word with no spaces used to name the packages"
    print "number_of_packages is an integer greater than one giving the number of packages to be generated.  EPICFILE is split into this many pieces."
    print "pkg_build_folder is the folder in which the packages will be built"
    sys.exit(2)
        
def getargs():
    # usage()  # Print usage information
    if len(sys.argv) < 6:
        usage()
	
    # Clean up command line arguments, since IDLE debug mode otherwise tries to process them
    # Example: idle -d -s -r extract_epic_data.py \
    #    '++dir=/Volumes/bes4.oic.ornl.gov/work/EPIC/OutputFileParsing/Test Files/'
    #    because otherwise, --dir will report an error that --dir is unrecognized
    logging.debug(len(sys.argv[1:]))
    for argc in range(1, len(sys.argv[1:]) + 1):
        argstr = sys.argv[argc]
        logging.debug(argstr)
        sys.argv[argc] = argstr.replace('+','-')
        logging.debug(sys.argv[argc])
        
    try:
        opts, args = getopt.getopt(sys.argv[1:], "r:f:t:n:o:", ["rundir=", "epicrun=", "tag=", "numpkgs=", "outdir="])
    except getopt.GetoptError:
        # print help information and exit
        print "Incorrect command line format"
        usage()
    
    opt_rundir=None
    opt_epicrun=None
    opt_tag=None
    opt_numpkgs=None
    opt_outdir=None
    
    for option, value in opts:
        if option in ("-r", "--rundir"):
            opt_rundir = value
        if option in ("-f", "--epicrun"):
            opt_epicrun = value
        if option in ("-t", "--tag"):
            opt_tag = value
        if option in ("-n", "--numpkgs"):
            opt_numpkgs = value
        if option in ("-o", "--outdir"):
            opt_outdir = value
            
    # Convert number of packages to an integer
    try:
       opt_numpkgs = int(opt_numpkgs)
    except:
       print "Failed to convert numpkgs to a number.  Must be an integer greater than 1."
       usage()
        
    if opt_rundir is None:
        usage()
    elif opt_epicrun is None:
        usage()
    elif opt_tag is None:
        usage()
    elif opt_numpkgs is None:
        usage()
    elif opt_outdir is None:
        usage()
    	
    return opt_rundir, opt_epicrun, opt_tag, opt_numpkgs, opt_outdir


