import os, pdb, sys
import pandas as pd
import numpy as np

base_dir = 'C:\\Users\\ritvik\\Desktop\\MyDocuments\\PhD\\Projects\\Grassland_Loss_PNAS\\Raw_Data\\USNC\\'
yld_fl   = 'Ylds_LS.csv'
dwoc_fl  = 'DWOC.csv'

df_y = pd.read_csv(base_dir+os.sep+yld_fl)
df_w = pd.read_csv(base_dir+os.sep+dwoc_fl)

df_y['yld'] = df_y['YIELD_N_0']/df_y['COUNT']
df_y = df_y[df_y['CDL']==2]
df_y = df_y[['LC','COUNT','yld']]
df_y.rename(columns={'yld':'N0_YLDF'}, inplace=True)


edges, labels = np.unique(df_w['N0_YLDF'], return_index=True)

edges = np.r_[-np.inf, edges + np.ediff1d(edges, to_end=np.inf)/2]
df_y['N0_DWOC'] = pd.cut(df_y['N0_YLDF'], bins=edges, labels=df_w['N0_DWOC'][labels])

print(df_y.head())
# df_y['N2O'] = df_y['N0_DWOC']*(1.0/15.0)*(0.01)*(44.0/28.0)

pdb.set_trace()
