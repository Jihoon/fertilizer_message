# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 14:36:18 2019

@author: min
"""
import numpy as np
import pandas as pd
import time

import ixmp as ix
import message_ix

from pathlib import Path
from message_ix.reporting import Reporter

import importlib
#import LoadParams
importlib.reload(LoadParams)

#%% Base model load

# launch the IX modeling platform using the local default database                                                                                                                       
mp = ix.Platform(dbprops=r'H:\MyDocuments\MESSAGE\message_ix\config\default.properties')

#modelName = "CD_Links_SSP2" # "BZ_MESSAGE_RU" #
#scenarioName = 'baseline' # "INDCi_1000-con-prim-dir-ncr" # 
#Sc_ref = message_ix.Scenario(mp, modelName, scenarioName)
#demand_fs_org = Sc_ref.par('demand', {"commodity":["i_feed"]})


# new model name in ix platform
modelName = "JM_GLB_NITRO"
basescenarioName =  "Baseline" # 'EmBound' #
newscenarioName = "TrdGlobal" # 

comment = "MESSAGE global test for new representation of nitrogen cycle with global trade"

Sc_nitro = message_ix.Scenario(mp, modelName, basescenarioName)

#%% Clone the model

Sc_nitro_trd = Sc_nitro_trd.clone(modelName, newscenarioName, comment)
#Sc_nitro_trd = message_ix.Scenario(mp, modelName, newscenarioName, 2)
#Sc_nitro_trd.par('bound_emission')
Sc_nitro_trd.remove_solution()
Sc_nitro_trd.check_out()

#%% Add tecs to set
# Only fertilizer traded for now (NH3 trade data not yet available)
comm_for_trd = ['Fertilizer Use|Nitrogen'] 
lvl_for_trd = ['material_final'] 
newtechnames_trd = ['NFert_trd']
newtechnames_imp = ['NFert_imp']
newtechnames_exp = ['NFert_exp']

#comm_for_trd = comm_for_trd # = ['NH3', 'Fertilizer Use|Nitrogen'] 
#newtechnames_trd = ['NH3_trd', 'NFert_trd']
#newtechnames_imp = ['NH3_imp', 'NFert_imp']
#newtechnames_exp = ['NH3_exp', 'NFert_exp']

Sc_nitro_trd.add_set("technology", newtechnames_trd + newtechnames_imp + newtechnames_exp)

cat_add = pd.DataFrame({'type_tec': ['import', 'export'],  # 'all' not need to be added here
                        'technology': newtechnames_imp + newtechnames_exp})

Sc_nitro_trd.add_set("cat_tec", cat_add)

#%% input & output

for t in newtechnames_trd:
    # output
    df = Sc_nitro_trd.par("output", {"technology":["coal_trd"]}) 
    df['technology'] = t
    df['commodity'] = comm_for_trd[newtechnames_trd.index(t)]
    df['value'] = 1
    df['unit'] = 'Tg N/yr'
#    df['level'] = newlevelnames[0]
    Sc_nitro_trd.add_par("output", df) 
    
    df = Sc_nitro_trd.par("input", {"technology":["coal_trd"]}) 
    df['technology'] = t
    df['commodity'] = comm_for_trd[newtechnames_trd.index(t)]
    df['value'] = 1
    df['unit'] = 'Tg N/yr'
#    df['level'] = newlevelnames[0]
    Sc_nitro_trd.add_par("input", df) 
    
reg = REGIONS.copy()
reg.remove('R11_GLB')

for t in newtechnames_imp:
    # output
    df = Sc_nitro_trd.par("output", {"technology":["coal_imp"], "node_loc":['R11_CPA']}) 
    df['technology'] = t
    df['commodity'] = comm_for_trd[newtechnames_imp.index(t)]
    df['value'] = 1
    df['unit'] = 'Tg N/yr'
    df['level'] = lvl_for_trd[newtechnames_imp.index(t)]
    for r in reg:
        df['node_loc'] = r    
        df['node_dest'] = r     
        Sc_nitro_trd.add_par("output", df) 
    # output
    df = Sc_nitro_trd.par("input", {"technology":["coal_imp"], "node_loc":['R11_CPA']}) 
    df['technology'] = t
    df['commodity'] = comm_for_trd[newtechnames_imp.index(t)]
    df['value'] = 1
    df['unit'] = 'Tg N/yr'
#    df['level'] = newlevelnames[newtechnames.index(t)]
    for r in reg:
        df['node_loc'] = r 
        Sc_nitro_trd.add_par("input", df)    
    
for t in newtechnames_exp:
    # output
    df = Sc_nitro_trd.par("output", {"technology":["coal_exp"], "node_loc":['R11_CPA']}) 
    df['technology'] = t
    df['commodity'] = comm_for_trd[newtechnames_exp.index(t)]
    df['value'] = 1
    df['unit'] = 'Tg N/yr'
#    df['level'] = newlevelnames[newtechnames_exp.index(t)]
    for r in reg:
        df['node_loc'] = r    
        Sc_nitro_trd.add_par("output", df) 
    # input
    df = Sc_nitro_trd.par("input", {"technology":["coal_exp"], "node_loc":['R11_CPA']}) 
    df['technology'] = t
    df['commodity'] = comm_for_trd[newtechnames_exp.index(t)]
    df['value'] = 1
    df['unit'] = 'Tg N/yr'
    df['level'] = lvl_for_trd[newtechnames_exp.index(t)]
    for r in reg:
        df['node_loc'] = r 
        df['node_origin'] = r    
        Sc_nitro_trd.add_par("input", df)         

# Need to incorporate the regional trade pattern

#%% Cost
    
for t in newtechnames_exp:
    df = Sc_nitro_trd.par("inv_cost", {"technology":["coal_exp"]}) 
    df['technology'] = t
    Sc_nitro_trd.add_par("inv_cost", df) 
    
    df = Sc_nitro_trd.par("var_cost", {"technology":["coal_exp"]}) 
    df['technology'] = t
    Sc_nitro_trd.add_par("var_cost", df) 
    
    df = Sc_nitro_trd.par("fix_cost", {"technology":["coal_exp"]}) 
    df['technology'] = t
    Sc_nitro_trd.add_par("fix_cost", df) 
      
for t in newtechnames_imp:
    df = Sc_nitro_trd.par("inv_cost", {"technology":["coal_imp"]}) 
    df['technology'] = t
    Sc_nitro_trd.add_par("inv_cost", df) 
    
    df = Sc_nitro_trd.par("var_cost", {"technology":["coal_imp"]}) 
    df['technology'] = t
    Sc_nitro_trd.add_par("var_cost", df) 
    
    df = Sc_nitro_trd.par("fix_cost", {"technology":["coal_imp"]}) 
    df['technology'] = t
    Sc_nitro_trd.add_par("fix_cost", df) 
    
for t in newtechnames_trd:    
    df = Sc_nitro_trd.par("var_cost", {"technology":["coal_trd"]}) 
    df['technology'] = t
    Sc_nitro_trd.add_par("var_cost", df) 
            
#%% Modify global emissions bound 
    
if basescenarioName == "EmBound":
    bound = 5000 #15000 #
    bound_emissions_2C = {
        'node': 'World',
        'type_emission': 'TCE',
        'type_tec': 'all',
        'type_year' : 'cumulative', #'2050', #
        'value': bound, #1076.0, # 1990 and on
        'unit' : 'tC',
    }
         
    df = pd.DataFrame(bound_emissions_2C, index=[0])
            
    Sc_nitro_trd.add_par("bound_emission", df) 

    
#%% Other background variables
    
  
paramList_tec = [x for x in Sc_nitro.par_list() if 'technology' in Sc_nitro.idx_sets(x)]
#paramList_comm = [x for x in Sc_nitro.par_list() if 'commodity' in Sc_nitro.idx_sets(x)]
params_exp = [x for x in paramList_tec if 'coal_exp' in set(Sc_nitro.par(x)["technology"].tolist())]
params_imp = [x for x in paramList_tec if 'coal_imp' in set(Sc_nitro.par(x)["technology"].tolist())]
params_trd = [x for x in paramList_tec if 'coal_trd' in set(Sc_nitro.par(x)["technology"].tolist())]
#params_trd = [x for x in paramList_comm if 'oil_extr1' in set(Sc_nitro.par(x)["technology"].tolist())]

a = set(params_exp + params_imp + params_trd) 
suffix = ('cost', 'put')
prefix = ('historical', 'ref', 'relation')
a = a - set([x for x in a if x.endswith(suffix)] + [x for x in a if x.startswith(prefix)] + ['emission_factor'])

for p in list(a):
    for t in newtechnames_exp:
        df = Sc_nitro_trd.par(p, {"technology":["coal_exp"]}) 
        df['technology'] = t
        Sc_nitro_trd.add_par(p, df)
                      
    for t in newtechnames_imp:
        df = Sc_nitro_trd.par(p, {"technology":["coal_imp"]}) 
        df['technology'] = t
        Sc_nitro_trd.add_par(p, df)
        
    for t in newtechnames_trd:
        df = Sc_nitro_trd.par(p, {"technology":["coal_trd"]}) 
        df['technology'] = t
        Sc_nitro_trd.add_par(p, df)
        
# Found coal_exp doesn't have full cells filled for technical_lifetime.
for t in newtechnames_exp:
    df = Sc_nitro_trd.par('technical_lifetime', {"technology":t, "node_loc":['R11_CPA']}) 
    for r in reg:
        df['node_loc'] = r   
        Sc_nitro_trd.add_par("technical_lifetime", df)       


#%% Histrorical trade activity
# Export capacity - understood as infrastructure enabling the trade activity (port, rail etc.)
        
# historical_activity     
N_trade = LoadParams.N_trade_R11.copy()      
  
df_histexp = N_trade.loc[(N_trade.Element=='Export') & (N_trade.year_act<2015),]        
df_histexp = df_histexp.assign(mode = 'M1') 
df_histexp = df_histexp.assign(technology = newtechnames_exp[0]) #t
df_histexp = df_histexp.drop(columns="Element")

df_histimp = N_trade.loc[(N_trade.Element=='Import') & (N_trade.year_act<2015),]    
df_histimp = df_histimp.assign(mode = 'M1') 
df_histimp = df_histimp.assign(technology = newtechnames_imp[0]) #t
df_histimp = df_histimp.drop(columns="Element")

# GLB trd historical activities (Now equal to the sum of imports)
#df_histimp.groupby(['year_act']).sum()
#df_histexp.groupby(['year_act']).sum()
dftrd = Sc_nitro_trd.par("historical_activity", {"technology":["coal_trd"]})
dftrd = dftrd.loc[(dftrd.year_act<2015) & (dftrd.year_act>2000),]
dftrd.value = df_histimp.groupby(['year_act']).sum().values
dftrd['unit'] = 'Tg N/yr'
dftrd['technology'] = newtechnames_trd[0]
Sc_nitro_trd.add_par("historical_activity", dftrd)
Sc_nitro_trd.add_par("historical_activity", df_histexp.append(df_histimp))

# historical_new_capacity
trdlife = Sc_nitro_trd.par("technical_lifetime", {"technology":["NFert_exp"]}).value[0]

df_histcap = df_histexp.drop(columns=['time', 'mode'])
df_histcap = df_histcap.rename(columns={"year_act":"year_vtg"})
df_histcap.value = df_histcap.value.values/trdlife

Sc_nitro_trd.add_par("historical_new_capacity", df_histcap)


#%%

# Adjust i_feed demand 
#demand_fs_org is the original i-feed in the reference SSP2 scenario
"""
In the scenario w/o trade, I assumed 100% NH3 demand is produced in each region.
Now with trade, I subtract the net import (of tN) from total demand, and the difference is produced regionally.
Still this does not include NH3 trade, so will not match the historical NH3 regional production.
Also, historical global production exceeds the global demand level from SSP2 scenario for the same year. 
I currently ignore this excess production and only produce what is demanded.
"""
df = demand_fs_org.loc[demand_fs_org.year==2010,:].join(LoadParams.N_feed.set_index('node'), on='node')
sh = pd.DataFrame( {'node': demand_fs_org.loc[demand_fs_org.year==2010, 'node'], 
                    'r_feed': df.totENE / df.value})    # share of NH3 energy among total feedstock (no trade assumed)
df = demand_fs_org.join(sh.set_index('node'), on='node')
df.value *= 1 - df.r_feed # Carve out the same % from tot i_feed values
df = df.drop('r_feed', axis=1)
Sc_nitro_trd.add_par("demand", df)



#%% Solve the scenario

Sc_nitro_trd.commit('Nitrogen Fertilizer for global model with fertilizer trade via global pool')

start_time = time.time()
#Sc_nitro_trd.to_gdx(r'..\..\message_ix\message_ix\model\data', "MsgData_"+Sc_nitro_trd.model+"_"+
#                Sc_nitro_trd.scenario+"_"+str(Sc_nitro_trd.version))

if basescenarioName == "EmBound":
    boundstr = str(bound)
else:
    boundstr = "NoBound"
        
Sc_nitro_trd.solve(model='MESSAGE', case=Sc_nitro_trd.model+"_"+
                Sc_nitro_trd.scenario + "_" + boundstr)

print(".solve: %.6s seconds taken." % (time.time() - start_time))

#%% utils
#Sc_nitro_trd.discard_changes()

#Sc_nitro_trd = message_ix.Scenario(mp, modelName, newscenarioName)


#%% Reporting for Andre@ESM
rep = Reporter.from_scenario(Sc_nitro_trd)

# Set up filters for N tecs
#rep.set_filters(t= newtechnames_ccs + newtechnames + ['NFert_imp', 'NFert_exp', 'NFert_trd'])

# NF demand summary
NF = rep.add_product('useNF', 'land_input', 'LAND')

print(rep.describe(rep.full_key('useNF')))
rep.get('useNF:n-y')
rep.write('useNF:n-y', 'nf_demand_'+boundstr+'.xlsx')
rep.write('useNF:y', 'nf_demand_total_'+boundstr+'.xlsx')
NF = rep.full_key('useNF')
def collapse(df):
    print(df)
    df['variable'] = 'Nitrogen demand' #df.pop('c')
#    df['scenario'] = df['scenario'] + '|' + df.pop('s')
    print(df, df.columns, df.loc[0,:])
    return df
a = rep.as_pyam('useNF:n-y', 'y', collapse=collapse)
rep.write(a[0], Path('nf_demand_'+boundstr+'_pyam.xlsx'))


# Output in pyam
rep.write('out:pyam', Path('activity_'+boundstr+'.xlsx'))

out_pyam = rep.get('out:pyam')
out_pyam.filter(variable='out|material_interim*').to_excel('NH3 production.xlsx')
out_pyam.filter(variable='out|material_final*').to_excel('NFert production.xlsx')
out_pyam.filter(variable='out|export*').to_excel('NFert export.xlsx')


# Input for N production
rep.set_filters()
rep.set_filters(t= newtechnames_ccs + newtechnames)
print(rep.describe(rep.full_key('in')))
rep.get('in:nl-ya-no-c')
def collapse_in(df):
    print(df)
    df['variable'] = 'input quantity' #df.pop('c')
#    df['scenario'] = df['scenario'] + '|' + df.pop('s')
    print(df, df.columns, df.loc[0,:])
    return df
a = rep.as_pyam('in:nl-ya-c', 'ya', collapse=collapse_in)
in_pyam = rep.get('in:nl-ya-c:iamc')
in_pyam.to_excel('NH3 production inputs.xlsx')


# Emissions for N production
print(rep.describe(rep.full_key('emi')))
rep.get('emi:nl-t-ya')
def collapse_emi(df):
    print(df)
    df['variable'] = 'input quantity' #df.pop('c')
#    df['scenario'] = df['scenario'] + '|' + df.pop('s')
    print(df, df.columns, df.loc[0,:])
    return df
a = rep.as_pyam('emi:nl-ya-c', 'ya', collapse=collapse_emi)
emi_pyam = rep.get('emi:nl-ya-c:iamc')
emi_pyam.to_excel('NH3 production emissions.xlsx')




# Price
rep.set_filters()
rep.set_filters(l= ['material_final', 'material_interim'])

print(rep.describe(rep.full_key('PRICE_COMMODITY')))
pc = rep.get(rep.full_key('PRICE_COMMODITY'))
def collapse_N(df):
    print(df, df.columns, df.loc[0,:], df.c)
    df['variable'] = 'Price|' + df.pop('c')
    print(df.loc[0,:])
    df.loc[df['l'] == "material_interim", 'unit'] = '$/tNH3'
    df.loc[df['l'] == "material_final", 'unit'] = '$/tN'
#    df['scenario'] = df['scenario'] + '|' + df.pop('s')
    print(df.loc[0,:])
    return df
a = rep.as_pyam('PRICE_COMMODITY:n-c-l-y', 'y', collapse=collapse_N)
rep.write(a[0], Path('price_commodity_'+boundstr+'.xlsx'))




#%%
# Reporting Test

LE = rep.add_product('emiss_land', 'land_emission', 'LAND')
print(rep.describe(rep.full_key('emiss_land')))
rep.set_filters(t=None, n=None, s=None)
rep.set_filters()
rep.set_filters(n=['R11_LAM'], e=['TCE'])
rep.write('emiss_land:n-s-y-e', Path('land_emission_LAM.xlsx'))


rep.set_filters(t=None, n=None, e=None)
rep.set_filters(nl=['R11_LAM'], e=['TCE'])
print(rep.describe(rep.full_key('emi')))
rep.get(rep.full_key('emi'))
rep.write('emi:nl-t-yv-ya-m-e-h', 'oth_emission_LAM.xlsx')


print(rep.describe('inv:t'))
rep.get(rep.full_key('out'))
rep.full_key('out')
rep.get('out:nl-t-ya')
b = rep.get('out:pyam')
rep.get('inv:nl-yv')
a = rep.get('inv:t-yv')
out = rep.describe('out')
rep.write('out:nl-t-ya', 'debug.xlsx')
rep.write('inv:pyam', Path('debug2.xlsx'))

out_pyam.scenarios()
out_pyam.regions()
out_pyam.variables(include_units=True)
out_pyam.filter(variable='out|material_interim|*', region='R11_CPA|R11_CPA').variables()
out_pyam.filter(level='1-').variables()
out_pyam.filter(variable='out|*', level=0,  region='R11_CPA|R11_CPA').variables()

out_pyam.filter(variable='out|material_interim*', region='R11_CPA|R11_CPA').line_plot(legend=False)
out_pyam.filter(variable='out|material_interim*', level=1,  region='R11_CPA|R11_CPA').line_plot(legend=True)
out_pyam.filter(variable='out|material_interim*', region='R11_CPA|R11_CPA').stack_plot()

out_pyam.filter(variable='out|material_interim*', region='R11_CPA|R11_CPA').to_excel('CPA.xlsx')

