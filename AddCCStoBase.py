# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 11:15:57 2019

@author: min
"""
import pandas as pd
import numpy as np
import time

import ixmp as ix
import message_ix

# Assume SetupNitrogenBase is run beforehand.
from SetupNitrogenBase import newtechnames, par_bgnd

#%% Load the base nitrogen scenario

# new model name in ix platform
modelName = "JM_GLB_NITRO"
basescenarioName = "Baseline" #
newscenarioName = "CCS_Base" # '2degreeC' # 

comment = "MESSAGE global test for new representation of nitrogen cycle with CCS"

# launch the IX modeling platform using the local default database                                                                                                                       
mp = ix.Platform(dbprops=r'H:\MyDocuments\MESSAGE\message_ix\config\default.properties')

Sc_nitro = message_ix.Scenario(mp, modelName, basescenarioName)

#%% Clone
Sc_nitro_ccs = Sc_nitro.clone(modelName, newscenarioName, comment)

Sc_nitro_ccs.remove_solution()
Sc_nitro_ccs.check_out()

#%% Add tecs to set
tec_for_ccs = list(newtechnames[i] for i in [0,2,3,4])
newtechnames_ccs = list(map(lambda x:str(x)+'_ccs', tec_for_ccs)) #include biomass in CCS, newtechnames[2:5]))
Sc_nitro_ccs.add_set("technology", newtechnames_ccs)

cat_add = pd.DataFrame({
        'type_tec': 'industry', #'non_energy' not in Russia model
        'technology': newtechnames_ccs
})

Sc_nitro_ccs.add_set("cat_tec", cat_add)



#%% Implement technologies - only for non-elec NH3 tecs

# input and output
# additional electricity input for CCS operation
df = Sc_nitro_ccs.par("input")
df = df[df['technology'].isin(tec_for_ccs)]
df['technology'] = df['technology'] + '_ccs'  # Rename the technologies
df.loc[df['commodity']=='electr', ['value']] = df.loc[df['commodity']=='electr', ['value']] + 0.005 # TUNE THIS # Add electricity input for CCS
Sc_nitro_ccs.add_par("input", df)   

df = Sc_nitro_ccs.par("output")
df = df[df['technology'].isin(tec_for_ccs)]
df['technology'] = df['technology'] + '_ccs'  # Rename the technologies
Sc_nitro_ccs.add_par("output", df)   




# Emission factors (emission_factor)

df = Sc_nitro_ccs.par("emission_factor")
biomass_ef = 0.942 # MtC/GWa from 109.6 kgCO2/GJ biomass (https://www.rvo.nl/sites/default/files/2013/10/Vreuls%202005%20NL%20Energiedragerlijst%20-%20Update.pdf)

# extract vent vs. storage ratio from h2_smr tec
h2_smr_vent_ratio = -Sc_nitro.par("relation_activity", {"relation":["CO2_cc"], "technology":["h2_smr_ccs"]}).value[0] \
                    / Sc_nitro.par("relation_activity", {"relation":["CO2_Emission"], "technology":["h2_smr_ccs"]}).value[0]
h2_coal_vent_ratio = -Sc_nitro.par("relation_activity", {"relation":["CO2_cc"], "technology":["h2_coal_ccs"]}).value[0] \
                    / Sc_nitro.par("relation_activity", {"relation":["CO2_Emission"], "technology":["h2_coal_ccs"]}).value[0]
h2_bio_vent_ratio = 1 + Sc_nitro.par("relation_activity", {"relation":["CO2_cc"], "technology":["h2_bio_ccs"]}).value[0] \
                    / (Sc_nitro.par("input", {"technology":["h2_bio_ccs"], "commodity":["biomass"]}).value[0] * biomass_ef)

# ef for NG
df_gas = df[df['technology']=='gas_NH3']
ef_org = np.asarray(df_gas.loc[df_gas['emission']=='CO2_transformation', ['value']])
df_gas = df_gas.assign(technology = df_gas.technology + '_ccs')
df_gas.loc[(df.emission=='CO2_transformation'), 'value'] = ef_org*h2_smr_vent_ratio 
df_gas.loc[(df.emission=='CO2'), 'value'] = ef_org*(h2_smr_vent_ratio-1)
Sc_nitro_ccs.add_par("emission_factor", df_gas)   

# ef for oil/coal
df_coal = df[df['technology'].isin(tec_for_ccs[2:])]
ef_org = np.asarray(df_coal.loc[df_coal['emission']=='CO2_transformation', ['value']])
df_coal = df_coal.assign(technology = df_coal.technology + '_ccs')
df_coal.loc[(df.emission=='CO2_transformation'), 'value'] = ef_org*h2_coal_vent_ratio 
df_coal.loc[(df.emission=='CO2'), 'value'] = ef_org*(h2_coal_vent_ratio-1)
Sc_nitro_ccs.add_par("emission_factor", df_coal)   

# ef for biomass
df_bio = df[df['technology']=='biomass_NH3']
biomass_input = Sc_nitro_ccs.par("input", {"technology":["biomass_NH3"], "commodity":["biomass"]}).value[0]
df_bio = df_bio.assign(technology = df_bio.technology + '_ccs')
df_bio['value'] = biomass_input*(h2_bio_vent_ratio-1)*biomass_ef 
Sc_nitro_ccs.add_par("emission_factor", df_bio)   




# Investment cost

df = Sc_nitro_ccs.par("inv_cost")

# Get inv_cost ratio between std and ccs for different h2 feedstocks
a = df[df['technology'].str.contains("h2_smr")].sort_values(["technology", "year_vtg"])  # To get cost ratio for std vs CCS
r_ccs_cost_gas = a.loc[(a.technology=='h2_smr') & (a.year_vtg >=2020)]['value'].values / a.loc[(a['technology']=='h2_smr_ccs') & (a.year_vtg >=2020)]['value'].values
r_ccs_cost_gas = r_ccs_cost_gas.mean()

a = df[df['technology'].str.contains("h2_coal")].sort_values(["technology", "year_vtg"])  # To get cost ratio for std vs CCS
r_ccs_cost_coal = a.loc[(a.technology=='h2_coal') & (a.year_vtg >=2020)]['value'].values / a.loc[(a['technology']=='h2_coal_ccs') & (a.year_vtg >=2020)]['value'].values
r_ccs_cost_coal = r_ccs_cost_coal.mean()

a = df[df['technology'].str.contains("h2_bio")].sort_values(["technology", "year_vtg"])  # To get cost ratio for std vs CCS
a = a[a.year_vtg > 2025] # h2_bio_ccs only available from 2030
r_ccs_cost_bio = a.loc[(a.technology=='h2_bio') & (a.year_vtg >=2020)]['value'].values / a.loc[(a['technology']=='h2_bio_ccs') & (a.year_vtg >=2020)]['value'].values
r_ccs_cost_bio = r_ccs_cost_bio.mean()

df_gas = df[df['technology']=='gas_NH3']
df_gas['technology'] = df_gas['technology'] + '_ccs'  # Rename the technologies
df_gas['value'] = df_gas['value']/r_ccs_cost_gas 
Sc_nitro_ccs.add_par("inv_cost", df_gas)   

df_coal = df[df['technology'].isin(tec_for_ccs[2:])]
df_coal['technology'] = df_coal['technology'] + '_ccs'  # Rename the technologies
df_coal['value'] = df_coal['value']/r_ccs_cost_coal 
Sc_nitro_ccs.add_par("inv_cost", df_coal) 

df_bio = df[df['technology']=='biomass_NH3']
df_bio['technology'] = df_bio['technology'] + '_ccs'  # Rename the technologies
df_bio['value'] = df_bio['value']/r_ccs_cost_bio 
Sc_nitro_ccs.add_par("inv_cost", df_bio) 




# Fixed cost

df = Sc_nitro_ccs.par("fix_cost")
df_gas = df[df['technology']=='gas_NH3']
df_gas['technology'] = df_gas['technology'] + '_ccs'  # Rename the technologies
df_gas['value'] = df_gas['value']/r_ccs_cost_gas # Same scaling (same 4% of inv_cost in the end)
Sc_nitro_ccs.add_par("fix_cost", df_gas)   

df_coal = df[df['technology'].isin(tec_for_ccs[2:])]
df_coal['technology'] = df_coal['technology'] + '_ccs'  # Rename the technologies
df_coal['value'] = df_coal['value']/r_ccs_cost_coal # Same scaling (same 4% of inv_cost in the end)
Sc_nitro_ccs.add_par("fix_cost", df_coal)  

df_bio = df[df['technology']=='biomass_NH3']
df_bio['technology'] = df_bio['technology'] + '_ccs'  # Rename the technologies
df_bio['value'] = df_bio['value']/r_ccs_cost_bio # Same scaling (same 4% of inv_cost in the end)
Sc_nitro_ccs.add_par("fix_cost", df_bio)  
      


# Emission factors (Relation)
 
# Gas
df = Sc_nitro_ccs.par("relation_activity")
df_gas = df[df['technology']=='gas_NH3'] # Originally all CO2_cc (truly emitted, bottom-up)
ef_org = df_gas.value.values.copy()
df_gas.value = ef_org * h2_smr_vent_ratio
df_gas = df_gas.assign(technology = df_gas.technology + '_ccs')
Sc_nitro_ccs.add_par("relation_activity", df_gas)   

df_gas.value = ef_org * (h2_smr_vent_ratio-1) # Negative
df_gas.relation = 'CO2_Emission'
Sc_nitro_ccs.add_par("relation_activity", df_gas)   

# Coal / Oil
df_coal = df[df['technology'].isin(tec_for_ccs[2:])] # Originally all CO2_cc (truly emitted, bottom-up)
ef_org = df_coal.value.values.copy()
df_coal.value = ef_org * h2_coal_vent_ratio
df_coal = df_coal.assign(technology = df_coal.technology + '_ccs')
Sc_nitro_ccs.add_par("relation_activity", df_coal)   

df_coal.value = ef_org * (h2_coal_vent_ratio-1) # Negative
df_coal.relation = 'CO2_Emission'
Sc_nitro_ccs.add_par("relation_activity", df_coal)   

# Biomass
df_bio = df[df['technology']=='biomass_NH3'] # Originally all CO2.cc (truly emitted, bottom-up)
df_bio.value = biomass_input*(h2_bio_vent_ratio-1)*biomass_ef
df_bio = df_bio.assign(technology = df_bio.technology + '_ccs')
Sc_nitro_ccs.add_par("relation_activity", df_bio)   

df_bio.relation = 'CO2_Emission'
Sc_nitro_ccs.add_par("relation_activity", df_bio)   


#%% Copy some bgnd parameters (values identical to _NH3 tecs)

par_bgnd_ccs = par_bgnd + ['technical_lifetime', 'capacity_factor', 'var_cost', 'growth_activity_lo']

for t in par_bgnd_ccs:
    df = Sc_nitro_ccs.par(t)
    df = df[df['technology'].isin(tec_for_ccs)]
    df['technology'] = df['technology'] + '_ccs'  # Rename the technologies
    Sc_nitro_ccs.add_par(t, df)   

#df = Sc_nitro.par('initial_activity_lo', {"technology":["gas_NH3"]})
#for q in newtechnames_ccs:
#    df['technology'] = q
#    Sc_nitro.add_par('initial_activity_lo', df)   
#           
#df = Sc_nitro.par('growth_activity_lo', {"technology":["gas_NH3"]})
#for q in newtechnames_ccs:
#    df['technology'] = q
#    Sc_nitro.add_par('growth_activity_lo', df)   
#    
#%% Solve the scenario

Sc_nitro_ccs.commit('Nitrogen Fertilizer for Russia Pilot')

start_time = time.time()
#Sc_nitro_ccs.to_gdx(r'..\..\message_ix\message_ix\model\data', "MsgData_"+Sc_nitro_ccs.model+"_"+
#                Sc_nitro_ccs.scenario+"_"+str(Sc_nitro_ccs.version))

Sc_nitro_ccs.solve(model='MESSAGE', case=Sc_nitro_ccs.model+"_"+
                Sc_nitro_ccs.scenario+"_"+str(Sc_nitro_ccs.version))

print(".solve: %.6s seconds taken." % (time.time() - start_time))
