import os, pdb

def replace_line(fl,line_num,text):
    # Read in text file
    lines = open(fl, 'r').readlines()
    # Replace text
    lines[line_num-1] = text

    # Write out text file
    out = open(fl, 'w')
    out.writelines(lines)
    out.close()

if __name__ == '__main__':
    replace_line('C:\\Users\\ritvik\\Documents\\PhD\\Projects\\EPIC\\Cedar_Creek - Copy\\395974.sol',17,'   00.05   00.05\n')
