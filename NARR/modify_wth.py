import os, pandas, pdb, numpy, csv

base_dir = 'C:\\Users\\ritvik\\Documents\\PhD\\Projects\\Lake_States\\Meta\\'
file = 'NLDAS_CDR.prn'

rng = [1.5,1.4,1.3,1.2,1.1,1.0,0.9,0.8,0.7,0.6,0.5]

df = pandas.read_fwf(base_dir+file, header=None, widths=[6,4,4,6,6,6,6,6,6])

for r in rng:
    print r
    out_fl = base_dir+file[:-4]+str(r)+'.prn'
    epic_out = open(out_fl,'w')
    for index, row in df.iterrows():
        tmp = float(row[6])*float(r)
        epic_out.write(('%6d%4d%4d%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f\n') % (row[0],row[1],row[2],row[3],row[4],row[5],tmp,row[7],row[8]))	
    epic_out.close()
