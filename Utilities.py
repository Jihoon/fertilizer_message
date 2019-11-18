# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 13:45:03 2019

@author: min
"""
import pandas as pd

def shift_model_horizon(scen, scen_base, fyear=2030, tecs):
    """Shift model horizon for technologies relevant for N-fertilizer

    This specific bound added to the scenario can be used to account
    for CO2 emissions.

    Parameters
    ----------
    scen : :class:`message_ix.Scenario`
        scenario to which changes should be applied
    scen_base : :class:`message_ix.Scenario`
        scenario from which values are read
    fyear : int
        year to be set as first model year 
    tecs : list
        names of technologies to be shifted  
    """

    df = scen_base.set('cat_year')
    df_cum = df.loc[df.type_year == "cumulative"].reset_index(drop=True)
    newhistyears = df_cum.year[df_cum.index[df_cum.year<fyear].tolist()].tolist()    # year to be set as last historical year 
    lasthistyear_org = df.year[df.type_year=="initializeyear_macro"]
    
    df = scen_base.var('ACT')    
    df_ACT = df[df.technology.isin(tecs) & df.year_act.isin(newhistyears)].groupby(['node_loc', 'technology', 'year_act']).sum().reset_index()
    df = scen_base.var('CAP_NEW')
    df_CAP_NEW = df[df.technology.isin(tecs) & df.year_vtg.isin(newhistyears)].groupby(['node_loc', 'technology', 'year_act']).sum().reset_index()
    df = scen_base.var('LAND')
    df_LAND = df[df.year.isin(newhistyears)].groupby(['node', 'land_scenario', 'year']).sum().reset_index()
        
# extraction already taken care of in policy scenarios
#    df = scen_base.var('EXT')
#    df_EXT = df[df.technology.isin(tecs) & df.year.isin(newhistyear)].groupby(['node_loc', 'technology', 'year_act']).sum().reset_index()
#    df_EXT = scen_base.var('EXT', {'year':lasthistyear}).groupby(['node', 'commodity', 'grade', 'year']).sum().reset_index()


    #%% Change first modeling year (dealing with the 5-year step scenario)
    
    df = scen.set('cat_year')
    a = df[((df.type_year=="firstmodelyear") & (df.year<fyear))]
#    a = df[((df.type_year=="cumulative") & (df.year<fyear)) | ((df.type_year=="firstmodelyear") & (df.year<fyear))]
    
    df.loc[df.type_year=='firstmodelyear', 'year'] = fyear
    scen.add_set("cat_year", df) 
    scen.remove_set("cat_year", a) 
    
    #%% Filling in history for 2020    
    
    # historical_activity
    df = scen.par('historical_activity', {'year_act':lasthistyear_org})
    #df = df[df.value > 0]
    a = pd.merge(df[['node_loc', 'technology', 'mode', 'time', 'unit']], 
                 df_ACT[['node_loc', 'technology', 'year_act', 'lvl']], how='right', on=['node_loc', 'technology']).rename(columns={'lvl':'value'})
    a = a[a.value > 0]
    a['unit'] = 'GWa'
    a['year_act'] = a['year_act'].astype(int)
    scen.add_par("historical_activity", a) 
    
    # historical_new_capacity
    df = scen.par('historical_new_capacity', {'year_vtg':lasthistyear_org})
    #df = df[df.value > 0]
    a = pd.merge(df[['node_loc', 'technology', 'unit']], 
                 df_CAP_NEW[['node_loc', 'technology', 'year_vtg', 'lvl']], how='right', on=['node_loc', 'technology']).rename(columns={'lvl':'value'})
    a = a[a.value > 0]
    a['year_vtg'] = a['year_vtg'].astype(int)
    scen.add_par("historical_new_capacity", a) 
    
    # historical_extraction
#    df = scen.par('historical_extraction', {'year':lasthistyear_org})
#    #df = df[df.value > 0]
#    a = pd.merge(df[['node', 'commodity', 'grade', 'unit']], 
#                 df_EXT[['node', 'commodity', 'grade', 'year', 'lvl']], how='outer', on=['node', 'commodity', 'grade']).rename(columns={'lvl':'value'})
#    a = a[a.value > 0]
#    a['unit'] = 'GWa'
#    a['year'] = a['year'].astype(int)
#    scen.add_par("historical_extraction", a) 
#    
    # historical_land
    df_LAND = df_LAND.rename(columns={'lvl':'value'}).drop(columns=['mrg'])
    df_LAND['unit'] = '%'
    scen.add_par("historical_land", df) 
