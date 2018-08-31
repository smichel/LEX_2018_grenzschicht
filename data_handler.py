# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 09:41:42 2018

@author: Henning
"""

import time 
import datetime
import sys
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, num2date
import matplotlib
import numpy as np
from os.path import join
from scipy.interpolate import interp1d
from matplotlib import dates
from processing_functions import read_data
from processing_functions import apply_correction
from processing_functions import data_interpolation_p_t
from processing_functions import get_gradients
from plot_functions import profile_plot_series
from plot_functions import gradient_profile_plot_series
""" This is the data_handler to analyse the measurements

"""

instrument_spef=0                                       #Instrument specification 0 for Arduinos, 1 for LIDAR, 2 for Radiosonde)
data_path="//192.168.206.173/lex2018/profil/Daten/"
file_name="20180831105131_Grenzschichtentwicklung2.npy"
file=data_path+file_name
ref=0                                                               
p_intv_no=20                                            # number of pressure levels to interpolate
plot_path="//192.168.206.173//lex2018/profil/Plots/Liveplots/"       

#==============================================================================
i=0
while True:
     time.sleep(1)
     i += 1
     print(i)
     if np.mod(i,60) == 0 :
         #run function profile_plot_series
         try:  
             if instrument_spef == 0:
                data=read_data(data_path,file_name)
            #data=data[0:12]
                data_calib=apply_correction(data)
                
                unit_time,p_levels,Temp_pint,RH_pint,Theta= data_interpolation_p_t(data_calib,ref,p_intv_no,instrument_spef)
                p_mid_levels,Temp_diff,Theta_diff,RH_diff=get_gradients(unit_time,p_levels,Temp_pint,Theta,RH_pint)
                profile_plot_series(file_name,plot_path,unit_time,p_levels,Temp_pint,RH_pint,Theta)
                if np.mod(i,300) == 0:
                    print("Start plotting Gradient Contoruf")
                    gradient_profile_plot_series(file_name,plot_path,unit_time,Temp_diff,Theta_diff,RH_diff,p_mid_levels)   
#Theta,p_levels,Temp_pint, unit_time = profile_plot_series(filename,ref,p_intv_no)
         except:
             print('NOPE...')
#==============================================================================




