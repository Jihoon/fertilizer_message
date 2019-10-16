# -*- coding: utf-8 -*-
"""
Created on Thu Oct 25 14:23:10 2018

@author: min
"""

import gdxpds

data_ready_for_GAMS = { 'symbol_name': df }

gdx_file = r'C:\Users\min\message_ix\message_ix\model\data\MsgData_New_AllReg_Hydro_5.gdx'
gdx = dataframes = gdxpds.to_dataframes(gdx_file)
