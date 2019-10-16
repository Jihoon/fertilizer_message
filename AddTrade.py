# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 14:36:18 2019

@author: min
"""
import numpy as np

N_trade_R14 = pd.read_csv(r'..\trade.FAO.R14.csv', index_col=0)

N_trade_R11 = pd.read_csv(r'..\trade.FAO.R11.csv', index_col=0)
N_trade_R11.msgregion = 'R11_' + N_trade_R11.msgregion
N_trade_R11.Value = N_trade_R11.Value/1e6
N_trade_R11.Unit = 'Tg N/yr' 
N_trade_R11 = N_trade_R11.assign(time = 'year') 
N_trade_R11 = N_trade_R11.rename(columns={"Value":"value", "Unit":"unit", "msgregion":"node_loc", "Year":"year_act"})

#%%
# new model name in ix platform
modelName = "JM_GLB_NITRO"
basescenarioName = '2degreeC' # "Baseline" #
newscenarioName = "Trade_Base" # 

comment = "MESSAGE global test for new representation of nitrogen cycle with global trade"

Sc_nitro = message_ix.Scenario(mp, modelName, basescenarioName)

#%% Clone
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
    
for t in newtechnames_imp:
    # output
    df = Sc_nitro_trd.par("output", {"technology":["coal_imp"]}) 
    df['technology'] = t
    df['commodity'] = comm_for_trd[newtechnames_imp.index(t)]
    df['value'] = 1
    df['unit'] = 'Tg N/yr'
    df['level'] = lvl_for_trd[newtechnames_imp.index(t)]
    Sc_nitro_trd.add_par("output", df) 
    # output
    df = Sc_nitro_trd.par("input", {"technology":["coal_imp"]}) 
    df['technology'] = t
    df['commodity'] = comm_for_trd[newtechnames_imp.index(t)]
    df['value'] = 1
    df['unit'] = 'Tg N/yr'
#    df['level'] = newlevelnames[newtechnames.index(t)]
    Sc_nitro_trd.add_par("input", df)    
    
for t in newtechnames_exp:
    # output
    df = Sc_nitro_trd.par("output", {"technology":["coal_exp"]})
    df['technology'] = t
    df['commodity'] = comm_for_trd[newtechnames_exp.index(t)]
    df['value'] = 1
    df['unit'] = 'Tg N/yr'
#    df['level'] = newlevelnames[newtechnames_exp.index(t)]
    Sc_nitro_trd.add_par("output", df) 
    # input
    df = Sc_nitro_trd.par("input", {"technology":["coal_exp"]})
    df['technology'] = t
    df['commodity'] = comm_for_trd[newtechnames_exp.index(t)]
    df['value'] = 1
    df['unit'] = 'Tg N/yr'
    df['level'] = lvl_for_trd[newtechnames_exp.index(t)]
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
    
#%% Other background variables
    
#for t in newtechnames_exp:
#    df = Sc_nitro_trd.par("capacity_factor", {"technology":["coal_exp"]}) 
#    df['technology'] = t
#    Sc_nitro_trd.add_par("capacity_factor", df)
#    
#    df = Sc_nitro_trd.par("technical_lifetime", {"technology":["coal_exp"]}) # lifetime = 15 year
#    df['technology'] = t
#    Sc_nitro_trd.add_par("technical_lifetime", df)      
#    
#          
#for t in newtechnames_imp:
#    df = Sc_nitro_trd.par("capacity_factor", {"technology":["coal_imp"]}) 
#    df['technology'] = t 
#    Sc_nitro_trd.add_par("capacity_factor", df)
#        
#for t in newtechnames_trd:
#    df = Sc_nitro_trd.par("capacity_factor", {"technology":["coal_trd"]}) 
#    df['technology'] = t
#    Sc_nitro_trd.add_par("capacity_factor", df)
#    
  
paramList_tec = [x for x in Sc_nitro.par_list() if 'technology' in Sc_nitro.idx_sets(x)]
#paramList_comm = [x for x in Sc_nitro.par_list() if 'commodity' in Sc_nitro.idx_sets(x)]
params_exp = [x for x in paramList_tec if 'coal_exp' in set(Sc_nitro.par(x)["technology"].tolist())]
params_imp = [x for x in paramList_tec if 'coal_imp' in set(Sc_nitro.par(x)["technology"].tolist())]
params_trd = [x for x in paramList_tec if 'coal_trd' in set(Sc_nitro.par(x)["technology"].tolist())]
#params_trd = [x for x in paramList_comm if 'oil_extr1' in set(Sc_nitro.par(x)["technology"].tolist())]

a = set(params_exp + params_imp + params_trd) 
suffix = ('cost', 'put')
prefix = ('historical', 'ref')
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
                Sc_nitro_trd.scenario+"_"+str(Sc_nitro_trd.version))

print(".solve: %.6s seconds taken." % (time.time() - start_time))

#%% utils
Sc_nitro_trd.discard_changes()

Sc_nitro_trd = message_ix.Scenario(mp, modelName, newscenarioName)
#reporting(mp, Sc_nitro_trd, 'False', modelName, newscenarioName, 
#                      merge_hist=True, xlsx=r'H:\MyDocuments\MESSAGE\message_data\tools\post_processing\MESSAGEix_WorkDB_Template.xlsx',
#                      out_dir=r'H:\MyDocuments\MESSAGE\message_ix\message_ix\model\output',)


rep = Reporter.from_scenario(Sc_nitro_trd)

rep.set_filters(t=['NFert_imp', 'NFert_exp', 'NFert_trd'])
rep.set_filters(t=newtechnames_ccs + newtechnames + ['NFert_imp', 'NFert_exp', 'NFert_trd'])
print(rep.describe('inv:t'))
rep.get(rep.full_key('out'))
rep.full_key('out')
rep.get('out:nl-t-ya')
rep.get('out:nl-t-ya:pyam')
rep.get('inv:nl-yv')
a = rep.get('inv:t-yv')
out = rep.describe('out')
rep.write('out:nl-t-ya', 'debug.xlsx')
rep.write('out:pyam', Path('debug2.xlsx'))
rep.write('inv:pyam', Path('debug2.xlsx'))

out_pyam = rep.get('out:pyam')
out_pyam.scenarios()
out_pyam.regions()
out_pyam.variables(include_units=True)
out_pyam.filter(variable='out|material_interim|*', region='R11_CPA|R11_CPA').variables()
out_pyam.filter(level='1-').variables()
out_pyam.filter(variable='out|*', level=0,  region='R11_CPA|R11_CPA').variables()

out_pyam.filter(variable='out|material_interim*', region='R11_CPA|R11_CPA').line_plot(legend=False)
out_pyam.filter(variable='out|material_interim*', level=1,  region='R11_CPA|R11_CPA').line_plot(legend=True)
out_pyam.filter(variable='out|material_interim*', region='R11_CPA|R11_CPA').stack_plot()

out_pyam.add_product('useNF', )