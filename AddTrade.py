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


#%% Import trade data (from FAO)

N_trade_R14 = pd.read_csv(r'..\trade.FAO.R14.csv', index_col=0)

N_trade_R11 = pd.read_csv(r'..\trade.FAO.R11.csv', index_col=0)
N_trade_R11.msgregion = 'R11_' + N_trade_R11.msgregion
N_trade_R11.Value = N_trade_R11.Value/1e6
N_trade_R11.Unit = 'Tg N/yr' 
N_trade_R11 = N_trade_R11.assign(time = 'year') 
N_trade_R11 = N_trade_R11.rename(columns={"Value":"value", "Unit":"unit", "msgregion":"node_loc", "Year":"year_act"})

#%% Base model load

# new model name in ix platform
modelName = "JM_GLB_NITRO"
basescenarioName = '2degreeC' # "Baseline" #
newscenarioName = "Trade_Global" # 

comment = "MESSAGE global test for new representation of nitrogen cycle with global trade"

# launch the IX modeling platform using the local default database                                                                                                                       
mp = ix.Platform(dbprops=r'H:\MyDocuments\MESSAGE\message_ix\config\default.properties')

Sc_nitro = message_ix.Scenario(mp, modelName, basescenarioName)

#%% Clone the model

Sc_nitro_trd = Sc_nitro.clone(modelName, newscenarioName, comment)

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
    # output
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
    # output
    df = Sc_nitro_trd.par("inv_cost", {"technology":["coal_imp"]}) 
    df['technology'] = t
    Sc_nitro_trd.add_par("inv_cost", df) 
    
    df = Sc_nitro_trd.par("var_cost", {"technology":["coal_imp"]}) 
    df['technology'] = t
    Sc_nitro_trd.add_par("var_cost", df) 
    
    df = Sc_nitro_trd.par("fix_cost", {"technology":["coal_imp"]}) 
    df['technology'] = t
    Sc_nitro_trd.add_par("fix_cost", df) 
    
    
#%% Regional cost calibration 
    
# Scaler based on WEO 2014 (based on IGCC tec)    
scaler_cost = pd.DataFrame(
    {'scaler': [1.00,	0.81,	0.96,	0.96,	0.96,	0.88,	0.81,	0.65,	0.42,	0.65,	1.12],
     'node_loc': ['R11_NAM',	
                'R11_LAM',	
                'R11_WEU',	
                'R11_EEU',	
                'R11_FSU',	
                'R11_AFR',	
                'R11_MEA',	
                'R11_SAS',	
                'R11_CPA',	
                'R11_PAS',	
                'R11_PAO']})
    
tec_scale = (newtechnames + newtechnames_ccs)
tec_scale = [e for e in tec_scale if e not in ('NH3_to_N_fertil', 'electr_NH3')]

# Scale all NH3 tecs in each region with the scaler
for t in tec_scale:    
    for p in ['inv_cost', 'fix_cost', 'var_cost']:
        df = Sc_nitro_trd.par(p, {"technology":t}) 
        temp = df.join(scaler_cost.set_index('node_loc'), on='node_loc')
        df.value = temp.value * temp.scaler
        Sc_nitro_trd.add_par(p, df) 
        
# For CPA, experiment to make the coal_NH3 cheaper than gas_NH3
for p in ['inv_cost', 'fix_cost']:#, 'var_cost']:
    df_c = Sc_nitro_trd.par(p, {"technology":'coal_NH3', "node_loc":"R11_CPA"}) 
    df_g = Sc_nitro_trd.par(p, {"technology":'gas_NH3', "node_loc":"R11_CPA"})
    df_f = Sc_nitro_trd.par(p, {"technology":'fueloil_NH3', "node_loc":"R11_CPA"})
    
    df_cc = Sc_nitro_trd.par(p, {"technology":'coal_NH3_ccs', "node_loc":"R11_CPA"}) 
    df_gc = Sc_nitro_trd.par(p, {"technology":'gas_NH3_ccs', "node_loc":"R11_CPA"})
    df_fc = Sc_nitro_trd.par(p, {"technology":'fueloil_NH3_ccs', "node_loc":"R11_CPA"})
#    r1 = df_g.value[0]/df_c.value[0]     # Constant over years
#    r2 = df_f.value[0]/df_c.value[0]     # Constant over years
    df_fc.value = df_cc.value * 0.91 # Gas/fueloil cost the same as coal
    df_gc.value = df_cc.value  # 'Let the fuel price decide.'
    df_cc.value = df_cc.value * 0.9 # 'Let the fuel price decide.'
    
    Sc_nitro_trd.add_par(p, df_g)
    Sc_nitro_trd.add_par(p, df_c)
    Sc_nitro_trd.add_par(p, df_f)
    Sc_nitro_trd.add_par(p, df_gc)
    Sc_nitro_trd.add_par(p, df_cc)
    Sc_nitro_trd.add_par(p, df_fc)
            
#%% Modify global emissions bound 
bound = 2000 #15000 #
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


#%% Histrorical activity
# Export capacity - understood as infrastructure enabling the trade activity (port, rail etc.)
        
# historical_activity 
df_histexp = N_trade_R11.loc[(N_trade_R11.Element=='Export') & (N_trade_R11.year_act<2015),]        
df_histexp = df_histexp.assign(mode = 'M1') 
df_histexp = df_histexp.assign(technology = newtechnames_exp[0]) #t
df_histexp = df_histexp.drop(columns="Element")

df_histimp = N_trade_R11.loc[(N_trade_R11.Element=='Import') & (N_trade_R11.year_act<2015),]    
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


#%% Solve the scenario

Sc_nitro_trd.commit('Nitrogen Fertilizer for global model with fertilizer trade via global pool')

start_time = time.time()
#Sc_nitro_trd.to_gdx(r'..\..\message_ix\message_ix\model\data', "MsgData_"+Sc_nitro_trd.model+"_"+
#                Sc_nitro_trd.scenario+"_"+str(Sc_nitro_trd.version))

Sc_nitro_trd.solve(model='MESSAGE', case=Sc_nitro_trd.model+"_"+
                Sc_nitro_trd.scenario+"_"+str(bound))

print(".solve: %.6s seconds taken." % (time.time() - start_time))

#%% utils
Sc_nitro_trd.discard_changes()

Sc_nitro_trd = message_ix.Scenario(mp, modelName, newscenarioName, 1)


#%% Reporting
rep = Reporter.from_scenario(Sc_nitro_trd)

# Set up filters for N tecs
rep.set_filters(t= newtechnames_ccs + newtechnames + ['NFert_imp', 'NFert_exp', 'NFert_trd'])

# NF demand summary
NF = rep.add_product('useNF', 'land_input', 'LAND')

print(rep.describe(rep.full_key('useNF')))
rep.get('useNF:n-y')
rep.write('useNF:n-y', 'nf_demand_2000.xlsx')
rep.write('useNF:y', 'nf_demand_tota_2000l.xlsx')



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





# Output in pyam
rep.write('out:pyam', Path('debug2.xlsx'))

out_pyam = rep.get('out:pyam')
out_pyam.filter(variable='out|material_interim*').to_excel('NH3.xlsx')
out_pyam.filter(variable='out|material_final*').to_excel('NFert.xlsx')
out_pyam.filter(variable='out|export*').to_excel('Export.xlsx')



# Test
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

