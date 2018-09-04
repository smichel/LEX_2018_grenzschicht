# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 09:41:42 2018

@author: Henning
"""

import time 
import datetime
import sys
import matplotlib.pyplot as plt
import typhon
from matplotlib.dates import date2num, num2date
import matplotlib
import numpy as np
from os.path import join
from scipy.interpolate import interp1d
from matplotlib import dates
from processing_functions import read_data
from processing_functions import apply_correction
from processing_functions import data_interpolation_p_t
from processing_functions import data_interpolation_z_t
from processing_functions import altitude
from processing_functions import get_gradients
from processing_functions import calc_specific_humidity, calc_pseudopot_temp, boundary_layer_height
from plot_functions import profile_plot_series
from plot_functions import alt_time_plot
from plot_functions import plot_timeseries
from plot_functions import gradient_profile_plot_series
from plot_functions import plot_boundary_layer_height

from matplotlib import dates





""" This is the data_handler to analyse the measurements

"""

instrument_spef=0                                       #Instrument specification 0 for Arduinos, 1 for LIDAR, 2 for Radiosonde)
data_path="//192.168.206.173/lex2018/profil/Daten/"
file_name="20180904124938_Grenzschichtentwicklung5.npy"
file=data_path+file_name
ref=0                                                               
p_intv_no=20 
z_intv_no=p_intv_no                                           # number of pressure levels to interpolate
plot_path="//192.168.206.173//lex2018/profil/Plots/Liveplots/"       

#==============================================================================
i=0
while True:
     time.sleep(1)
     i += 1
     print(i)
     if np.mod(i,10) == 0 :
         #run function profile_plot_series
         #try:  
             if instrument_spef == 0:
                data=read_data(data_path,file_name)
            #data=data[0:12]
            
            ###for p coordinates
                data_calib=apply_correction(data)
                unit_time,p_levels,Temp_pint,RH_pint,Theta= data_interpolation_p_t(data_calib,ref,p_intv_no,instrument_spef)
                p_mid_levels,Temp_diff,Theta_diff,RH_diff=get_gradients(unit_time,p_levels,Temp_pint,Theta,RH_pint)
                #profile_plot_series(file_name,plot_path,unit_time,p_levels,Temp_pint,RH_pint,Theta,True)
                #plot_timeseries(data,file_name,plot_path)
                if np.mod(i,120) == 0:
                    print("Start plotting Gradient Contoruf")
                    gradient_profile_plot_series(file_name,plot_path,unit_time,Temp_diff,Theta_diff,RH_diff,p_mid_levels)
                    print("Plotted Gradients and stored them on server")
                if np.mod(i,10) == 0:
                    print('Estimate boundary layer height')
                    z_BL_q, p_BL_q = boundary_layer_height(RH_pint, Temp_pint, p_levels, 'specific_humidity')
                    z_BL_rh,p_BL_rh=boundary_layer_height(RH_pint, Temp_pint, p_levels, 'relative_humidity')
                    z_BL_theta,p_BL_theta=boundary_layer_height(RH_pint,Temp_pint,p_levels,'potential_temperature')
                    z_BL_theta_e,p_BL_theta_e=boundary_layer_height(RH_pint,Temp_pint,p_levels,'pseudopotential_temperature')
                    #plot_boundary_layer_height(file_name,plot_path,unit_time,z_BL_rh,z_BL_q,z_BL_theta,z_BL_theta_e)
                    #print("Plotted Boundary layer height and stored them on server")
             
                
             ###for z coordinates
                #if np.mod(i,60)==0:
                    print('Plot in z-coordinates')
                    unit_time,z_levels,Temp_zint,RH_zint,Theta= data_interpolation_z_t(data_calib,ref,z_intv_no,instrument_spef)  
                    alt_time_plot(file_name,plot_path,unit_time,z_levels,Temp_zint,RH_zint,Theta,z_BL_q,z_BL_rh,z_BL_theta,z_BL_theta_e,boundary_layer=True)
             
#Theta,p_levels,Temp_pint, unit_time = profile_plot_series(filename,ref,p_intv_no)
         #except:
          #   print('NOPE...')
#==============================================================================




