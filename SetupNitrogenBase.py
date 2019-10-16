# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# load required packages 
# import itertools
import pandas as pd

import matplotlib.pyplot as plt
plt.style.use('ggplot')

import ixmp as ix
import message_ix

import os
#import numpy as np
import time, re

os.chdir(r'H:\MyDocuments\MESSAGE\message_data')
from tools.post_processing.iamc_report_hackathon import report as reporting

from message_ix.reporting import Reporter

os.chdir(r'H:\MyDocuments\MESSAGE\N-fertilizer\code.Global')

#import LoadParams # Load techno-economic param values from the excel file
exec(open(r'LoadParams.py').read())

#%% Set up scope

# details for existing datastructure to be updated and annotation log in database 
modelName = "CD_Links_SSP2" # "BZ_MESSAGE_RU" #
scenarioName = 'baseline' # "INDCi_1000-con-prim-dir-ncr" # 
#verbase = 10

# new model name in ix platform
newmodelName = "JM_GLB_NITRO"
newscenarioName = "Baseline" # '2degreeC' # 

comment = "CD_Links_SSP2 test for new representation of nitrogen cycle"

REGIONS = [
    'R11_AFR',
    'R11_CPA',
    'R11_EEU',
    'R11_FSU',
    'R11_LAM',
    'R11_MEA',
    'R11_NAM',
    'R11_PAO',
    'R11_PAS',
    'R11_SAS',
    'R11_WEU',
    'R11_GLB' ]


#msg_reg_short = {'AFR', 'CPA', 'EEU', 'FSU', 'LAM', 'MEA', 'NAM', 'PAO', 'PAS', 'SAS', 'WEU'}
#msg_reg = ["R11_" + x for x in msg_reg_short]

#%% Load scenario

# launch the IX modeling platform using the local default database                                                                                                                       
mp = ix.Platform(dbprops=r'H:\MyDocuments\MESSAGE\message_ix\config\default.properties')

# Reference scenario
Sc_ref = message_ix.Scenario(mp, modelName, scenarioName)
paramList_tec = [x for x in Sc_ref.par_list() if 'technology' in Sc_ref.idx_sets(x)]
params_src = [x for x in paramList_tec if 'solar_i' in set(Sc_ref.par(x)["technology"].tolist())]

#%% Clone
Sc_nitro = Sc_ref.clone(newmodelName, newscenarioName)
#Sc_nitro = message_ix.Scenario(mp, newmodelName, newscenarioName)
Sc_nitro.remove_solution()
Sc_nitro.check_out()


#%% Add new technologies & commodities

newtechnames = ['biomass_NH3', 'electr_NH3', 'gas_NH3', 'coal_NH3', 'fueloil_NH3', 'NH3_to_N_fertil']
newcommnames = ['NH3', 'Fertilizer Use|Nitrogen'] #'N-fertilizer'
newlevelnames = ['material_interim', 'material_final']

Sc_nitro.add_set("technology", newtechnames)
Sc_nitro.add_set("commodity", newcommnames)
Sc_nitro.add_set("level", newlevelnames)
Sc_nitro.add_set("type_tec", 'industry')

cat_add = pd.DataFrame({
        'type_tec': 'industry', #'non_energy' not in Russia model
        'technology': newtechnames
})

Sc_nitro.add_set("cat_tec", cat_add)


#%% Connect input & output

### NH3 production process
for t in newtechnames[0:5]:
    # output
    df = Sc_nitro.par("output", {"technology":["solar_i"]}) # lifetime = 15 year
    df['technology'] = t
    df['commodity'] = newcommnames[0]
    df['level'] = newlevelnames[0]
    Sc_nitro.add_par("output", df) 
    df['commodity'] = 'd_heat'
    df['level'] = 'secondary'      
    df['value'] = output_heat[newtechnames.index(t)] 
    Sc_nitro.add_par("output", df) 
      
    # Fuel input
    df = df.rename(columns={'time_dest':'time_origin', 'node_dest':'node_origin'})
    if t=='biomass_NH3':
        lvl = 'primary'
    else:
        lvl = 'secondary'
    df['level'] = lvl
    # Non-elec fuels
    if t[:-4]!='electr': # electr has only electr input (no other fuel)
        df['commodity'] = t[:-4] # removing '_NH3'    
        df['value'] = input_fuel[newtechnames.index(t)] 
        Sc_nitro.add_par("input", df)         
    # Electricity input (for any fuels)
    df['commodity'] = 'electr' # All have electricity input    
    df['value'] = input_elec[newtechnames.index(t)] 
    df['level'] = 'secondary'
    Sc_nitro.add_par("input", df)        
    
    # Water input # Not exist in Russia model - CHECK for global model
#    df['level'] = 'water_supply' # final for feedstock input     
#    df['commodity'] = 'freshwater_supply' # All have electricity input    
#    df['value'] = input_water[newtechnames.index(t)] 
#    Sc_nitro.add_par("input", df)            
    
    df = Sc_nitro.par("technical_lifetime", {"technology":["solar_i"]}) # lifetime = 15 year
    df['technology'] = t
    Sc_nitro.add_par("technical_lifetime", df)   
    
    # Costs
    df = Sc_nitro.par("inv_cost", {"technology":["solar_i"]})
    df['technology'] = t
    df['value'] = inv_cost[newtechnames.index(t)] 
    Sc_nitro.add_par("inv_cost", df) 
    
    df = Sc_nitro.par("fix_cost", {"technology":["solar_i"]})
    df['technology'] = t
    df['value'] = fix_cost[newtechnames.index(t)] 
    Sc_nitro.add_par("fix_cost", df)  
    
    df = Sc_nitro.par("var_cost", {"technology":["solar_i"]})
    df['technology'] = t
    df['value'] = var_cost[newtechnames.index(t)] 
    Sc_nitro.add_par("var_cost", df)   
    
    # Emission factor
    df = Sc_nitro.par("output", {"technology":["solar_i"]})
    df = df.drop(columns=['node_dest', 'commodity', 'level', 'time'])
    df = df.rename(columns={'time_dest':'emission'})
    df['emission'] = 'CO2_transformation' # Check out what it is
    df['value'] = emissions[newtechnames.index(t)] 
    df['technology'] = t
    df['unit'] = '???'
    Sc_nitro.add_par("emission_factor", df)   
    df['emission'] = 'CO2' # Check out what it is
    df['value'] = 0 # Set the same as CO2_transformation
    Sc_nitro.add_par("emission_factor", df) 
    
    # Emission factors in relation (Currently these are more correct values than emission_factor)
    df = Sc_nitro.par("relation_activity",  {"relation":["CO2_cc"], "technology":["h2_smr"]})
    df['value'] = emissions[newtechnames.index(t)] 
    df['technology'] = t
    df['unit'] = '???'
    Sc_nitro.add_par("relation_activity", df)   
#    df = Sc_nitro.par("relation_activity",  {"relation":["CO2_cc"], "technology":t})
#    Sc_nitro.remove_par("relation_activity",  df)

    # Capacity factor
    df = Sc_nitro.par("capacity_factor", {"technology":["solar_i"]})
    df['technology'] = t
    df['value'] = capacity_factor[newtechnames.index(t)] 
    Sc_nitro.add_par("capacity_factor", df)   



### N-fertilizer from NH3
comm = newcommnames[-1]
tech = newtechnames[-1]

# output  
df = Sc_nitro.par("output", {"technology":["solar_i"]}) 
df['technology'] = tech
df['commodity'] = comm #'N-fertilizer'  
df['level'] = newlevelnames[-1] #'land_use_reporting'
Sc_nitro.add_par("output", df)     
 
# input
df = Sc_nitro.par("output", {"technology":["solar_i"]}) 
df = df.rename(columns={'time_dest':'time_origin', 'node_dest':'node_origin'})
df['technology'] = tech
df['level'] = newlevelnames[0] 
df['commodity'] = newcommnames[0] #'NH3'     
df['value'] = input_fuel[newtechnames.index(tech)] # NH3/N = 17/14
Sc_nitro.add_par("input", df)  
    
df = Sc_nitro.par("technical_lifetime", {"technology":["solar_i"]}) # lifetime = 15 year
df['technology'] = tech
Sc_nitro.add_par("technical_lifetime", df)   

# Costs
df = Sc_nitro.par("inv_cost", {"technology":["solar_i"]})
df['value'] = inv_cost[newtechnames.index(tech)]
df['technology'] = tech
Sc_nitro.add_par("inv_cost", df) 

df = Sc_nitro.par("fix_cost", {"technology":["solar_i"]})
df['technology'] = tech
df['value'] = fix_cost[newtechnames.index(tech)]
Sc_nitro.add_par("fix_cost", df)  

df = Sc_nitro.par("var_cost", {"technology":["solar_i"]})
df['technology'] = tech
df['value'] = var_cost[newtechnames.index(tech)]
Sc_nitro.add_par("var_cost", df)   


#%% Copy some background parameters# 

par_bgnd = [x for x in params_src if '_up' in x] + [x for x in params_src if '_lo' in x] 
par_bgnd = list(set(par_bgnd) - set(['level_cost_activity_soft_lo', 'level_cost_activity_soft_up', 'growth_activity_lo', 'soft_activity_lo', 'soft_activity_up']))
for t in par_bgnd[:-1]:
    df = Sc_nitro.par(t, {"technology":["solar_i"]}) # lifetime = 15 year
    for q in newtechnames:
        df['technology'] = q
        Sc_nitro.add_par(t, df)   
        
df = Sc_nitro.par('initial_activity_lo', {"technology":["gas_extr_mpen"]})
for q in newtechnames:
    df['technology'] = q
    Sc_nitro.add_par('initial_activity_lo', df)   
           
df = Sc_nitro.par('growth_activity_lo', {"technology":["gas_extr_mpen"]})
for q in newtechnames:
    df['technology'] = q
    Sc_nitro.add_par('growth_activity_lo', df)      
# Initial new capacity needed (I guess)
#df = Sc_nitro.par("initial_activity_up", {"technology":["gas_extr_4"]}) 
#df = df.rename(columns={'year_act':'year_vtg'})
#df['value'] = 0.1 # PLACEHOLDER
#df['technology'] = 'electr_NH3'
#df = df.drop(columns=['time'])
#Sc_nitro.add_par("initial_new_capacity_up", df)   
#    
#df = Sc_nitro.par("growth_new_capacity_up", {"technology":["coal_ppl"]}) 
#df['value'] = 0.05 # PLACEHOLDER
#df['technology'] = 'electr_NH3'
#Sc_nitro.add_par("growth_new_capacity_up", df)   

#%% Process the regional historical activities
        
feedshare_GLO.insert(1, "bio_pct", 0)
feedshare_GLO.insert(2, "elec_pct", 0)
# 17/14 NH3:N ratio, to get NH3 activity based on N demand => No NH3 loss assumed during production
feedshare_GLO.iloc[:,1:6] = input_fuel[5] * feedshare_GLO.iloc[:,1:6] 
feedshare_GLO.insert(6, "NH3_to_N", 1)

# Share of feedstocks for NH3 prodution (based on 2010 => Assumed fixed for any past years)
feedshare = feedshare_GLO.sort_values(['Region']).set_index('Region').drop('R11_GLB')
        
# Get historical N demand from SSP2-nopolicy (may need to vary for diff scenarios)
N_demand = N_demand_GLO[N_demand_GLO.Scenario=="NoPolicy"].reset_index().loc[0:10,2010] # 2010 tot N demand
N_demand = N_demand.repeat(len(newtechnames))

act2010 = (feedshare.values.flatten() * N_demand).reset_index(drop=True)

#N_demand = (N_demand_GLO[N_demand_GLO.Scenario=="NoPolicy"].reset_index().loc[0:10,2020] 
#            + N_demand_GLO[N_demand_GLO.Scenario=="NoPolicy"].reset_index().loc[0:10,2010])/2
#N_demand = N_demand.repeat(len(newtechnames))
#
#act2015 = (feedshare.values.flatten() * N_demand).reset_index(drop=True)


#%% Historical activities/capacities - Region specific

df = Sc_nitro.par("historical_activity").iloc[0:len(newtechnames)*(len(REGIONS)-1),] # Choose whatever same number of rows
df['technology'] = newtechnames * (len(REGIONS)-1)
df['value'] = act2010 # total NH3 or N in Mt 2010 FAO Russia 
df['year_act'] = 2010
df['node_loc'] = [y for x in REGIONS[:-1] for y in (x,)*len(newtechnames)]
df['unit'] = 'Tg N/yr' # Separate unit needed for NH3?
Sc_nitro.add_par("historical_activity", df)

# 2015 activity necessary if this is 5-year step scenario
#df['value'] = act2015 # total NH3 or N in Mt 2010 FAO Russia 
#df['year_act'] = 2015
#Sc_nitro.add_par("historical_activity", df)

life = Sc_nitro.par("technical_lifetime", {"technology":["gas_NH3"]}).value[0]

df = Sc_nitro.par("historical_new_capacity").iloc[0:len(newtechnames)*(len(REGIONS)-1),] # whatever
df['technology'] = newtechnames * (len(REGIONS)-1)
df['value'] = [x * 1/life/capacity_factor[0] for x in act2010] # Assume 1/lifetime (=15yr) is built each year
df['year_vtg'] = 2010
df['unit'] = 'Tg N/yr'
Sc_nitro.add_par("historical_new_capacity", df)
#df['value'] = [x * 1/15/capacity_factor[0] for x in act2015] # Assume 1/lifetime is built each year
#df['year_vtg'] = 2015
#Sc_nitro.add_par("historical_new_capacity", df)


#%% Secure feedstock balance (foil_fs, gas_fs, coal_fs)  loil_fs?
# Select only the model years
years = set(map(int, list(Sc_nitro.set('year')))) & set(N_demand_GLO) # get intersection 
#scenarios = N_demand_FSU.Scenario # Scenario names (SSP2)
N_demand = N_demand_GLO.loc[N_demand_GLO.Scenario=="NoPolicy",].drop(35)
N_demand = N_demand[N_demand.columns.intersection(years)]
N_demand[2110] = N_demand[2100] # Make up 2110 data (for now) in Mt/year

# Assume a fixed share of FSU is for RUS
#N_demand_RUS = N_demand_GLO.iloc[2,]/N_demand_GLO.iloc[2,][2010]*hist_activity2010[5] # Baseline: 66% of FSU production is Russia (\\hdrive\home$\u045\min\MyDocuments\MESSAGE\N-fertilizer\FAOSTAT)

# Turn it into a df and join
#N_demand = N_demand.T
#N_demand.index.name = 'year'
#N_demand_GLO = N_demand_GLO.reset_index().rename(index=str, columns={2: "value"})

# Now with the 5-year interval model. Need to interpolate for the intermediate years.

#from scipy.interpolate import interp1d
##N_demand_10yr = N_demand_RUS[~N_demand_RUS.value.isna()]
#f=interp1d(N_demand_GLO.year, N_demand_10yr.value)
#N_demand_RUS.value = f(N_demand_RUS.year)
#N_demand_RUS.loc[N_demand_RUS.year==2015,['value']] = hist_activity2015[5]

# Adjust i_feed demand (10% of total feedstock for Ammonia assumed) - REFINE
demand_fs_org = Sc_nitro.par('demand', {"commodity":["i_feed"]})
demand_fs_org['value'] = demand_fs_org['value'] * 0.9
Sc_nitro.add_par("demand", demand_fs_org)

df = Sc_nitro.par("demand", {"commodity":["i_feed"]})
df = df.loc[df.year>=2000,].reset_index(drop=True).sort_values(['node', 'year'])
df['commodity'] = newcommnames[-1]
df['level'] = newlevelnames[-1]
df['unit'] = 'Tg N/yr'
#df = df.drop("value", axis=1)
#df = df.join(N_demand_RUS.set_index('year'), on='year')
df.value = N_demand.values.flatten()

Sc_nitro.add_par("demand", df)   


#%% Solve the model.

Sc_nitro.commit('Nitrogen Fertilizer for Global model - no policy')

start_time = time.time()

#Sc_nitro.to_gdx(r'..\..\message_ix\message_ix\model\data', "MsgData_"+Sc_nitro.model+"_"+
#                Sc_nitro.scenario+"_"+str(Sc_nitro.version))

# I do this because the current set up doesn't recognize the model path correctly.
Sc_nitro.solve(model='MESSAGE', case=Sc_nitro.model+"_"+
                Sc_nitro.scenario+"_"+str(Sc_nitro.version))
#Sc_ref.solve(model='MESSAGE', case=Sc_ref.model+"_"+Sc_ref.scenario+"_"+str(Sc_ref.version))


print(".solve: %.6s seconds taken." % (time.time() - start_time))



#%% Run reference model

#
#start_time = time.time()
#Sc_ref.remove_solution()
#Sc_ref.solve(model='MESSAGE', case=Sc_ref.model+"_"+
#                Sc_ref.scenario+"_"+str(Sc_ref.version))
#print(".solve: %.6s seconds taken." % (time.time() - start_time))
#
