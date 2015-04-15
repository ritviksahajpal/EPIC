##################################################################
# SSURGO_to_csv.py Apr 2015
# ritvik sahajpal (ritvik@umd.edu)
# 
##################################################################
import constants, logging, os, us, csv, pdb, glob
import numpy as np
import pandas as pd

def component_aggregation(group):  
    # Sort by depth, makes it easier to process later
    group.sort('hzdept_r',inplace=True)
    
    # Determine number of soil layers
    list_depths       = np.append(group['hzdepb_r'],group['hzdept_r'])
    num_layers        = len(np.unique(list_depths))-1 # Exclude 0    
    if(num_layers <= 0):
        logging.info('Incorrect number of soil layers '+str(num_layers)+' '+str(group['cokey']))
        return

    return group

def read_ssurgo_tables(soil_dir):    
    # Read in SSURGO data
    pd_mapunit   = pd.read_csv(soil_dir+os.sep+constants.MAPUNIT+'.txt'  ,sep=constants.SSURGO_SEP,header=None,usecols=constants.mapunit_vars.keys())
    pd_component = pd.read_csv(soil_dir+os.sep+constants.COMPONENT+'.txt',sep=constants.SSURGO_SEP,header=None,usecols=constants.component_vars.keys())
    pd_chorizon  = pd.read_csv(soil_dir+os.sep+constants.CHORIZON+'.txt' ,sep=constants.SSURGO_SEP,header=None,usecols=constants.chorizon_vars.keys())    
    pd_muaggatt  = pd.read_csv(soil_dir+os.sep+constants.MUAGGATT+'.txt' ,sep=constants.SSURGO_SEP,header=None,usecols=constants.muaggatt_vars.keys())
    pd_chfrags   = pd.read_csv(soil_dir+os.sep+constants.CHFRAGS+'.txt'  ,sep=constants.SSURGO_SEP,header=None,usecols=constants.chfrags_vars.keys())

    # Rename dataframe columns from integers to SSURGO specific names
    pd_mapunit.rename(columns=constants.mapunit_vars    ,inplace=True)
    pd_component.rename(columns=constants.component_vars,inplace=True)
    pd_chorizon.rename(columns=constants.chorizon_vars  ,inplace=True)
    pd_muaggatt.rename(columns=constants.muaggatt_vars  ,inplace=True)
    pd_chfrags.rename(columns=constants.chfrags_vars    ,inplace=True)    

    # Sum up Fragvol_r in pd_chfrags
    # See http://www.nrel.colostate.edu/wiki/nri/images/2/21/Workflow_NRI_SSURGO_2010.pdf
    pd_chfrags = pd_chfrags.groupby('chkey').sum().reset_index(level=0)

    # Aggregate pd_chorizon data based on cokey
    chorizon_agg = pd_chorizon.groupby('cokey').apply(component_aggregation)    

    # Join chfrags and chorizon_agg data
    chfrags_chor = chorizon_agg.merge(pd_chfrags,left_on='chkey',right_on='chkey')

    # Join chfrags_chor data to the component table
    ccomp = chfrags_chor.merge(pd_component,left_on='cokey',right_on='cokey')

    # Join the chor_comp data to pd_muaggatt table
    muag_ccomp = ccomp.merge(pd_muaggatt,left_on='mukey',right_on='mukey')

    # Join muag_ccomp to mapunit data
    map_data   = muag_ccomp.merge(pd_mapunit,left_on='mukey',right_on='mukey')

    return map_data

def SSURGO_to_csv():
    sgo_data = pd.DataFrame()
    # Read file containing list of states to process
    fname = constants.base_dir+os.sep+'input'+os.sep+constants.LIST_STATES

    with open(fname, 'rb') as f:
        reader  = csv.reader(f)
        list_st = list(reader)

    for st in list_st:
        logging.info(st[0])

        # For each state, process the SSURGO tabular files
        for dir_name, subdir_list, file_list in os.walk(constants.data_dir):
            if('_'+st[1]+'_' in dir_name and constants.TABULAR in subdir_list):
                logging.info(dir_name[-3:]) # County FIPS code

                tmp_df           = read_ssurgo_tables(dir_name+os.sep+constants.TABULAR)  
                tmp_df['state']  = st[1]
                tmp_df['county'] = dir_name[-3:]
                tmp_df['FIPS']   = int(us.states.lookup(st[1]).fips+dir_name[-3:])
                sgo_data         = pd.concat([tmp_df,sgo_data],ignore_index =True)                

    # Drop columns with all missing values
    sgo_data.dropna(axis=1,how='all',inplace=True)
    # Replace hydgrp values with integers
    sgo_data.replace(constants.hydgrp_vars,inplace=True)    

    # If any null values exist, replace with mean of value in mukey
    df3 = pd.DataFrame()
    logging.info('If any null values exist, replace with mean of value in mukey')
    if(np.any(sgo_data.isnull())):
        df1 = sgo_data.set_index('mukey')
        df2 = sgo_data.groupby('mukey').mean()
        df3 = df1.combine_first(df2)

        # If any null values remain, replace by county mean
        logging.info('If any null values remain, replace by county mean')
        if(np.any(df3.isnull())):     
            df1      = df3.reset_index().set_index('FIPS')
            cnt_mean = sgo_data.groupby(['FIPS']).mean()
            df3      = df1.combine_first(cnt_mean)
        else:
            pass

            # If any null values remain, replace by state mean
            logging.info('If any null values remain, replace by state mean')
            if(np.any(df3.isnull())):
                df1     = df3.reset_index().set_index('state')
                st_mean = sgo_data.groupby(['state']).mean()
                df3     = df1.combine_first(st_mean)
            else:
                pass
    else:
        pass

    df3.reset_index(inplace=True)
    # Convert niccdcd and hydgrp to integers
    df3['hydgrp']  = df3['hydgrp'].astype(int)
    df3['niccdcd'] = df3['niccdcd'].astype(int)

    # Drop components with non zero initial depth
    logging.info('Drop faulty components')
    drop_df = df3.groupby('cokey').filter(lambda x: x['hzdept_r'].min() <= 0)

    logging.info('Select the dominant component')
    dom_df = drop_df.reset_index().groupby('mukey').apply(lambda g: g[g['comppct_r']==g['comppct_r'].max()])

    drop_df.to_csv(constants.out_dir+'drop.csv')
    df3.to_csv(constants.out_dir+'all.csv')
    dom_df.to_csv(constants.out_dir+'dominant.csv')
    logging.info('Done!')
    return dom_df

def write_epic_soil_file(group):
    if(not(os.path.isfile(constants.t_soil_dir+str(group.mukey.iloc[0])+'.sol'))):
        epic_file  = open(constants.t_soil_dir+str(group.mukey.iloc[0])+'.sol', 'w')
        num_layers = len(group.hzdepb_r)

        # Line 1
        epic_file.write(str(group.mukey.iloc[0])+' State: '+str(group.state.iloc[0])+' FIPS: '+str(group.FIPS.iloc[0])+'\n')
        # Line 2
        epic_file.write('{:8.2f}{:8.2f}{:8.2f}{:8.2f}{:8.2f}{:8.2f}{:8.2f}{:8.2f}{:8.2f}{:8.2f}\n'.format(\
                        group.albedodry_r.iloc[0],group.hydgrp.iloc[0],0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0))
        # Line 3
        epic_file.write('{:8.2f}{:8.2f}{:8.2f}{:8.2f}{:8.2f}{:8.2f}{:8.2f}{:8.2f}{:8.2f}\n'.format(\
                        0.0,0.0,100.0,0.0,0.0,0.0,0.0,0.0,0.0))
        # Soil characteristics per soil layer
        epic_file.write(''.join(['{:8.2f}'.format(n*constants.CONV_DEPTH) for n in group.hzdepb_r])+'\n') # Depth to bottom of layer (m)
        epic_file.write(''.join(['{:8.2f}'.format(n) for n in group.dbthirdbar_r])+'\n')        # Bulk Density (T/m^3)
        epic_file.write(''.join(['{:8.2f}'.format(n) for n in group.wfifteenbar_r])+'\n')       # Soil water content at wilting point (1500 KPA), (m/m)
        epic_file.write(''.join(['{:8.2f}'.format(n) for n in group.wthirdbar_r])+'\n')         # Water content at field capacity (33 KPA), (m/m)
        epic_file.write(''.join(['{:8.2f}'.format(n) for n in group.sandtotal_r])+'\n')         # Sand content (%)
        epic_file.write(''.join(['{:8.2f}'.format(n) for n in group.silttotal_r])+'\n')         # Silt content (%)
        epic_file.write(''.join(['{:8.2f}'.format(n) for n in np.zeros(num_layers)])+'\n')      # Initial Org N concentration (g/T)   ---zeros---
        epic_file.write(''.join(['{:8.2f}'.format(n) for n in group.ph1to1h2o_r])+'\n')         # Soil pH ()
        epic_file.write(''.join(['{:8.2f}'.format(n) for n in group.sumbases_r])+'\n')          # Sum of bases (cmol/kg)
        epic_file.write(''.join(['{:8.2f}'.format(n*constants.CONV_OM_TO_WOC) for n in group.om_r])+'\n') # Organic matter content (%)
        epic_file.write(''.join(['{:8.2f}'.format(n) for n in group.caco3_r])+'\n')             # CaCO3 content (%)
        epic_file.write(''.join(['{:8.2f}'.format(n) for n in group.cec7_r])+'\n')              # Cation exchange capacity (cmol/kg)
        epic_file.write(''.join(['{:8.2f}'.format(n) for n in group.Fragvol_r])+'\n')           # Coarse fragment content (% by vol)
        epic_file.write(''.join(['{:8.2f}'.format(n) for n in np.zeros(num_layers)])+'\n')      # Initial NO3 conc (g/T)              ---zeros---
        epic_file.write(''.join(['{:8.2f}'.format(n) for n in np.zeros(num_layers)])+'\n')      # Initial Labile P (g/T)              ---zeros---
        epic_file.write(''.join(['{:8.2f}'.format(n) for n in np.zeros(num_layers)])+'\n')      # Crop residue (T/ha)                 ---zeros---
        epic_file.write(''.join(['{:8.2f}'.format(n) for n in group.dbovendry_r])+'\n')         # Oven dry Bulk Density (T/m^3)
        epic_file.write(''.join(['{:8.2f}'.format(n) for n in np.zeros(num_layers)])+'\n')      #                                     ---zeros---                       
        epic_file.write(''.join(['{:8.2f}'.format(n*constants.CONV_KSAT) for n in group.ksat_r])+'\n')    # Saturated conductivity (mm/h)

        for i in range(constants.ZERO_LINES):
            epic_file.write(''.join(['{:8.2f}'.format(n) for n in np.zeros(num_layers)])+'\n')
        
        # EPIC constant lines
        epic_file.write('\n\n\n')
        epic_file.write('    275.    200.    150.    140.    130.    120.    110.\n')
        epic_file.write('    0.20    0.40    0.50    0.60    0.80    1.00    1.20\n')
        epic_file.write('    .004    .006    .008    .009    .010    .010    .010\n')
        epic_file.close()
    else:
        logging.info('File exists: '+constants.t_soil_dir+str(group.mukey.iloc[0])+'.sol')

def csv_to_EPIC(df):
    try:
        df.groupby('mukey').apply(write_epic_soil_file)
    except Exception,e: 
        logging.info(str(e))
    
    # Output ieSlList.dat
    epic_SlList_file = open(constants.out_dir+os.sep+constants.SLLIST, 'w')

    idx = 1
    for filename in glob.iglob(os.path.join(constants.t_soil_dir, '*.sol')):
        epic_SlList_file.write(('%5s     Soils\\%-20s\n')%(idx,os.path.basename(filename)))
        idx += 1
    epic_SlList_file.close()

if __name__ == '__main__':
    df = SSURGO_to_csv()
    csv_to_EPIC(df)

#def uniq_vals(group):
#    try:
#        return group[group['cokey'] == mode(np.array(group.cokey))[0][0]]
#    except Exception, e:
#        logger.info(e)

#def wavg(val_col_name, wt_col_name):    
#    def inner(group):        
#        return (group[val_col_name] * group[wt_col_name]).sum() / group[wt_col_name].sum()
#    inner.__name__ = val_col_name
#    return inner

#def wt_mean(group):
#    # custom function for calculating a weighted mean
#    # values passed in should be vectors of equal length
#    g = group.groupby('layer_id')
#    for key,val in epic_soil_vars.iteritems():
#        group[val] = group[val] / g[val].transform('sum') * group['compct_r']

#    return group 

#def average_mukey_soil_vars(group):
#    return group.mean(numeric_only=True)

    
#df4 = pd.DataFrame()    
#df5 = pd.DataFrame()    
#logger.info('Compute weighted means')
#for key,val in epic_soil_vars.iteritems():
#    print val
#    df4[val] = df3.groupby(['mukey','layer_id']).apply(wavg(val, 'comppct_r'))

#cols    = [col for col in df4.columns if col not in ['mukey', 'layer_id']]
#tmp_df4 = df4[cols]
#df3.reset_index(inplace=True)
#df4.reset_index(inplace=True)
    
#df5 = df3[df3.columns.difference(tmp_df4.columns)]
#df6 = df5.groupby('mukey').apply(uniq_vals)
#df7 = df4.merge(df6,on=['mukey','layer_id'])
#df3.to_csv(out_dir+'SSURGO3.csv')            
#df4.to_csv(out_dir+'SSURGO4.csv')            
#df5.to_csv(out_dir+'SSURGO5.csv')
#df6.to_csv(out_dir+'SSURGO6.csv')
#df7.to_csv(out_dir+'SSURGO7.csv')
#logger.info('Done!')
#pdb.set_trace()

#logger.info('Done!')
