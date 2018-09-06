# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 09:41:42 2018

@author: Henning
"""

import time 
import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, num2date
import matplotlib
import numpy as np
from os.path import join
from scipy.interpolate import interp1d
from matplotlib import dates
from plot_functions import profile_plot_series
from processing_functions import read_data
from processing_functions import apply_correction
from processing_functions import data_interpolation_p_t, data_interpolation_z_t
from processing_functions import get_gradients
from processing_functions import altitude
from processing_functions import calc_specific_humidity, calc_pseudopot_temp, boundary_layer_height, smooth_variable
#from plot_functions import profile_plot_series
#from plot_functions import gradient_profile_plot_series
""" This is the data_handler to analyse the measurements

"""

instrument_spef=0                                       #Instrument specification 0 for Arduinos, 1 for LIDAR, 2 for Radiosonde)
data_path="//192.168.206.173/lex2018/messdaten/alpaka/data/20180829062417_Grenzschichtentwicklung/"
#data_path = "//192.168.206.173/lex2018/profil/Daten/"
#file_name="20180903132225_Grenzschichtentwicklung4_2.npy"
file_name="20180829062417_Grenzschichtentwicklung.npy"
file=data_path+file_name
ref=0                                                               
p_intv_no=20                                            # number of pressure levels to interpolate
plot_path="//192.168.206.173//lex2018/profil/Plots/BL_height/"       

start_time = datetime.datetime(2018, 8, 29, 7, 50)
end_time = datetime.datetime(2018, 8, 29, 14, 50)
#==============================================================================

data=read_data(data_path, file_name)
# apply calibration
data_calib=apply_correction(data)

# interpolate on pressure levels and a unit time 

unit_time,p_levels,Temp_pint,RH_pint,Theta= data_interpolation_p_t(data_calib,ref,p_intv_no,instrument_spef)
unit_time,z_levels,Temp_pint,RH_pint,Theta= data_interpolation_z_t(data_calib,ref,p_intv_no,instrument_spef)
# calculate gradients
p_mid_levels,Temp_diff,Theta_diff,RH_diff=get_gradients(unit_time,p_levels,Temp_pint,Theta,RH_pint)

N = 70
unit_time_smooth = smooth_variable(unit_time, N)
Temp_pint_smooth = smooth_variable(Temp_pint, N)
RH_pint_smooth = smooth_variable(RH_pint, N)
Theta_smooth = smooth_variable(Theta, N)

profile_plot_series(file_name,plot_path,unit_time_smooth,p_levels,Temp_pint_smooth,RH_pint_smooth,Theta_smooth, boundary_layer=True, start_time=start_time, end_time=end_time)
#z_BL, p_BL = boundary_layer_height(RH_pint, Temp_pint, p_levels, 'relative_humidity')
## calculate altitudes
#z_levels = np.zeros(Temp_pint.shape)
#z_mid_levels = np.zeros(RH_diff.shape)
#for t in range(len(unit_time)):
#    z_levels[:, t] = altitude(p_levels[::-1], Temp_pint[:, t][::-1], z0=7)
#
## flip altitude array to have the same orientation as p_levels and Temp_pint
#z_levels = z_levels[::-1]
#
#for lev in range(len(z_levels)-1):
#    z_mid_levels[lev] = (z_levels[lev] + z_levels[lev+1]) / 2_
#
## 1. attempt:
## find maximum in RH gradient
#RH_diff[np.isnan(RH_diff)] = -9999
#RH_diff_max_idx = np.nanargmax(RH_diff[:-2], axis=0) 
#p_BL_RH = np.array([p_mid_levels[i] for i in RH_diff_max_idx])
#
#
#
## 2. attempt
## calculate gradient of specific humidity
#
## calculate specific humidity from relative  humidity
#specific_hum = calc_specific_humidity(RH_pint, Temp_pint,np.tile(p_levels,(len(unit_time),1)).transpose())
#
#specific_hum_diff=np.diff(specific_hum, axis=0)
#specific_hum_diff[np.isnan(specific_hum_diff)] = -9999
#specific_hum_diff_max_idx = np.nanargmax(specific_hum_diff[:-2], axis=0)
#p_BL_q = np.array([p_mid_levels[i] for i in specific_hum_diff_max_idx])
#
## 3. attempt
## calculate gradient of potential temperature
#Theta_diff[np.isnan(Theta_diff)] = 9999
#pot_temp_diff_min_idx = np.nanargmin(Theta_diff[5:-2], axis=0) + 5
#p_BL_pot_temp = np.array([p_mid_levels[i] for i in pot_temp_diff_min_idx])
#
## 4. attempt
## calculate gradient of pseudopotential temperature
#pseudopot_temp = calc_pseudopot_temp(RH_pint, Temp_pint, np.tile(p_levels,(len(unit_time),1)).transpose())
#pseudopot_temp_diff=np.diff(pseudopot_temp, axis=0)
#fig, ax = plt.subplots()
#ax.imshow(pseudopot_temp, aspect='auto')
#pseudopot_temp_diff[np.isnan(pseudopot_temp_diff)] = -9999
#pseudopot_temp_diff_min_idx = np.nanargmax(pseudopot_temp_diff[5:-2], axis=0) + 5
#p_BL_pseudopot_temp = np.array([p_mid_levels[i] for i in pseudopot_temp_diff_min_idx])
#
#z_BL_RH = np.zeros(p_BL_RH.shape)
#z_BL_specific_hum = np.zeros(p_BL_RH.shape)
#z_BL_pot_temp = np.zeros(p_BL_RH.shape)
#z_BL_pseudopot_temp = np.zeros(p_BL_RH.shape)
#
#for t in range(len(unit_time)):
#    arg = RH_diff_max_idx[t]
#    arg2 = specific_hum_diff_max_idx[t]
#    arg3 = pot_temp_diff_min_idx[t]
#    arg4 = pseudopot_temp_diff_min_idx[t]
#    z_BL_RH[t] = z_mid_levels[arg, t]
#    z_BL_specific_hum[t] = z_mid_levels[arg2, t]
#    z_BL_pot_temp[t] = z_mid_levels[arg3, t]
#    z_BL_pseudopot_temp[t] = z_mid_levels[arg4, t]
##
## plot
#plt.rcParams.update({'font.size': 14})  
#fig, ax = plt.subplots()
#ax.plot(num2date(unit_time), z_BL_RH, label='Relative Humidity')
#ax.set_xlabel('Time')
#ax.set_ylabel('Boundary Layer Height [m]')
#ax.set_xticks(ax.get_xticks()[::])
#ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
#
#ax.plot(num2date(unit_time), z_BL_specific_hum, label='Specific Humidity')
#ax.plot(num2date(unit_time), z_BL_pot_temp, label='Potential Temperature')
#ax.plot(num2date(unit_time), z_BL_pseudopot_temp, label='Pseudopotential Temperature')
#ax.set_xlim(datetime.datetime(2018, 8, 29, 7, 50), datetime.datetime(2018, 8, 29, 14, 50))
##ax.set_xlim(datetime.datetime(2018, 9, 3, 13, 40), datetime.datetime(2018, 9, 3, 16, 30))
##ax[1].set_xlabel('Time')
##ax[1].set_ylabel('Boundary Layer Height [m]')
##ax[1].set_xticks(ax[0].get_xticks()[::])
##ax[1].xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
#ax.legend()



#==============================================================================




