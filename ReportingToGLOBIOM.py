"""
Creating outputs for GLOBIOM input
"""

from message_ix.reporting import Reporter
from pathlib import Path
import pandas as pd

import ixmp as ix
import message_ix

#%% Constants

#scen_names = {"baseline" : "NoPolicy",
#              "NPiREF-con-prim-dir-ncr" : "NPi",
#             "NPi2020_1600-con-prim-dir-ncr" : "NPi2020_1600",
##              "NPi2020_1000-con-prim-dir-ncr" : "NPi2020_1000",
#              "NPi2020_400-con-prim-dir-ncr" : "NPi2020_400"}

scen_names = ["baseline",
              "NPi2020-con-prim-dir-ncr",
              "NPi2020_1600-con-prim-dir-ncr",
#              "NPi2020_1000-con-prim-dir-ncr",
              "NPi2020_400-con-prim-dir-ncr"]

newtechnames = ['biomass_NH3', 'electr_NH3', 'gas_NH3', 'coal_NH3', 'fueloil_NH3', 'NH3_to_N_fertil']
tec_for_ccs = list(newtechnames[i] for i in [0,2,3,4])
newtechnames_ccs = list(map(lambda x:str(x)+'_ccs', tec_for_ccs)) #include biomass in CCS, newtechnames[2:5]))


#%%
ix.reporting.configure(units={'replace': {'???': '', '-':''}}) # '???' and '-' are not handled in pyint(?)


model_name = 'JM_GLB_NITRO_MACRO'
scen_name = scen_names[3]

mp = ix.Platform(dbprops=r'H:\MyDocuments\MESSAGE\message_ix\config\default.org.properties')


def GenerateOutput(scen, rep):
    
    rep.set_filters()
    rep.set_filters(t= newtechnames_ccs + newtechnames)

    # 1. Total NF demand
    rep.add_product('useNF', 'land_input', 'LAND')
    
    def collapse(df):
        df['variable'] = 'Nitrogen demand'
        df['unit'] = 'Mt N/yr'
        return df
    
    a = rep.convert_pyam('useNF:n-y', 'y', collapse=collapse)
    rep.write(a[0], Path('nf_demand_'+scen+'.xlsx'))

    """
    'emi' not working with filters on NH3 technologies for now.
    """
    # 2. Total emissions
    rep.set_filters()
    rep.set_filters(t= (newtechnames_ccs + newtechnames)[:-1]) # and NH3_to_N_fertil does not have emission factor

    def collapse_emi(df):
        print(df)
        df['variable'] = 'Emissions|CO2' 
        df['unit'] = 'Mt CO2'
        print(df, df.columns, df.loc[0,:])
        return df
    a = rep.convert_pyam('emi:nl-t-ya', 'ya', collapse=collapse_emi)
    rep.write(a[0], Path('nf_emissions_'+scen+'.xlsx'))


    # 3. Total inputs (incl. final energy) to fertilizer processes
    rep.set_filters()
    rep.set_filters(t= (newtechnames_ccs + newtechnames), c=['coal', 'gas', 'electr', 'biomass', 'fueloil']) 
        
    def collapse_in(df):
        df['variable'] = 'Final energy|'+df.pop('c')
        df['unit'] = 'GWa'
        return df
    a = rep.convert_pyam('in:nl-ya-c', 'ya', collapse=collapse_in)
    rep.write(a[0], Path('nf_input_'+scen+'.xlsx'))   
             
    # 4. Commodity price
    rep.set_filters()
    rep.set_filters(l= ['material_final', 'material_interim'])
    
    def collapse_N(df):
        df.loc[df['c'] == "NH3", 'unit'] = '$/tNH3'
        df.loc[df['c'] == "Fertilizer Use|Nitrogen", 'unit'] = '$/tN'
        df['variable'] = 'Price|' + df.pop('c')
        return df
    
    a = rep.convert_pyam('PRICE_COMMODITY:n-c-y', 'y', collapse=collapse_N)
    rep.write(a[0], Path('price_commodity_'+scen+'.xlsx'))

for sc in scen_names:
    Sc_ref = message_ix.Scenario(mp, model_name, sc)
    repo = Reporter.from_scenario(Sc_ref)
    GenerateOutput(sc, repo)
    
for cases in ['nf_demand', 'nf_emissions', 'nf_input', 'price_commodity']:
    infiles = []
    for sc in scen_names:
        infiles.append(pd.read_excel(cases + "_" + sc + ".xlsx"))        
    appended_df = pd.concat(infiles, join='outer', sort=False)
    appended_df.to_excel(cases+".xlsx", index=False)

#%% Emissions for N production
rep = Reporter.from_scenario(Sc_ref)

print(rep.describe(rep.full_key('emi')))
rep.describe('message:default')
rep.set_filters()
rep.set_filters(t= (newtechnames_ccs + newtechnames)[:-1]) # and NH3_to_N_fertil does not have emission factor
rep.set_filters(t= newtechnames[3]) # and NH3_to_N_fertil does not have emission factor
rep.set_filters(t= ['biomass_NH3']) # and NH3_to_N_fertil does not have emission factor
rep.set_filters(t= ['coal_adv'], e='CO2_transformation') # and NH3_to_N_fertil does not have emission factor

print(rep.describe(rep.full_key('emission_factor')))
rep.get(rep.full_key('emission_factor'))

a = Sc_ref.par('emission_factor', {'technology':'coal_adv', 'emission':'CO2_transformation'})
a = Sc_ref.par('emission_factor', {'technology':'coal_adv'})
b = Sc_ref.par('emission_factor', {'technology':'coal_NH3', 'emission':'CO2_transformation'})




print(rep.describe(rep.full_key('ACT')))
rep.get(rep.full_key('ACT'))

rep.get('emi:ya')
rep.write('emi:nl-t-ya', 'nf_emission_'+scen_name+'.xlsx') # This is working without any filter.

rep.write('emi:iamc', 'nf_emission_'+boundstr+'.xlsx') # as_pyam, iamc not working for the moment
def collapse_emi(df):
    print(df)
    df['variable'] = 'input quantity' 
    print(df, df.columns, df.loc[0,:])
    return df
a = rep.convert_pyam('emi:nl-t-ya', 'ya', collapse=collapse_emi)
rep.write(a[0], ('nf_emissions_'+scen_name+'_pyam.xlsx'))

