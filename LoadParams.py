# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 12:01:47 2019

@author: min

Load parameters for the new technologies
"""

import pandas as pd

# Read parameters in xlsx
te_params = pd.read_excel(r'..\n-fertilizer_techno-economic.xlsx', sheet_name='Sheet1')
n_inputs_per_tech = 12 # Number of input params per technology

inv_cost = te_params[2010][list(range(0, te_params.shape[0], n_inputs_per_tech))].reset_index(drop=True)
fix_cost = te_params[2010][list(range(1, te_params.shape[0], n_inputs_per_tech))].reset_index(drop=True)
var_cost = te_params[2010][list(range(2, te_params.shape[0], n_inputs_per_tech))].reset_index(drop=True)
technical_lifetime = te_params[2010][list(range(3, te_params.shape[0], n_inputs_per_tech))].reset_index(drop=True)
input_fuel = te_params[2010][list(range(4, te_params.shape[0], n_inputs_per_tech))].reset_index(drop=True)
input_fuel[0:5] = input_fuel[0:5] * 0.0317 # 0.0317 GWa/PJ, GJ/t = PJ/Mt
input_elec = te_params[2010][list(range(5, te_params.shape[0], n_inputs_per_tech))].reset_index(drop=True)
input_elec = input_elec * 0.0317 # 0.0317 GWa/PJ
input_water = te_params[2010][list(range(6, te_params.shape[0], n_inputs_per_tech))].reset_index(drop=True)
output_NH3 = te_params[2010][list(range(7, te_params.shape[0], n_inputs_per_tech))].reset_index(drop=True)
output_water = te_params[2010][list(range(8, te_params.shape[0], n_inputs_per_tech))].reset_index(drop=True)
output_heat = te_params[2010][list(range(9, te_params.shape[0], n_inputs_per_tech))].reset_index(drop=True)
output_heat = output_heat * 0.0317 # 0.0317 GWa/PJ
emissions = te_params[2010][list(range(10, te_params.shape[0], n_inputs_per_tech))].reset_index(drop=True) * 12 / 44 # CO2 to C
capacity_factor = te_params[2010][list(range(11, te_params.shape[0], n_inputs_per_tech))].reset_index(drop=True)


#%% Demand scenario [Mt/year] from GLOBIOM
N_demand_FSU = pd.read_excel(r'..\CD-Links SSP2 N-fertilizer demand.FSU.xlsx', sheet_name='data', nrows=3)
N_demand_GLO = pd.read_excel(r'..\CD-Links SSP2 N-fertilizer demand.Global.xlsx', sheet_name='data')

# NH3 feedstock share by region in 2010 (from http://ietd.iipnetwork.org/content/ammonia#benchmarks)
feedshare_GLO = pd.read_excel(r'..\Ammonia feedstock share.Global.xlsx', sheet_name='Sheet2', skiprows=13)

