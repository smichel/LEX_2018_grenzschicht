# -*- coding: utf-8 -*-
"""
Created on Wed Sep  5 11:59:38 2018

@author: Henning
"""


"""
This function compare the alpaca boundary layer heights to the ceilometer boundary height
"""
import csv
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
from processing_functions import smooth_variable
from plot_functions import profile_plot_series
from plot_functions import alt_time_plot
from plot_functions import plot_timeseries
from plot_functions import gradient_profile_plot_series
from plot_functions import plot_boundary_layer_height
from matplotlib import dates

#def compare_alpaca_bl_to_ceilometer()
def compare_alpaca_bl_to_ceilometer(day,month):
#day="31"
#month="08"
    instrument_spef=0                                       #Instrument specification 0 for Arduinos, 1 for LIDAR, 2 for Radiosonde)
    data_path="//192.168.206.173/lex2018/profil/Daten/"
    date=["29","31","01","03","04","05"]
        #indices = [i for i, s in enumerate(date) if '31' in s]
    l = [date.index(i) for i in date if day in i]
    idx=int(l[0])+1
    
    date_alpaca=["20180829062417","20180831105131","20180901095651","20180903095623","20180904124938","20180905094034"]
    file_name_alpaca=date_alpaca[l[0]]+"_Grenzschichtentwicklung"+str(idx)+".npy"
    file=data_path+file_name_alpaca
    ref=0                                                               
    p_intv_no=20 
    z_intv_no=p_intv_no                                           # number of pressure levels to interpolate
    plot_path="//192.168.206.173//lex2018/profil/Plots/Liveplots/"       
    
    #    #==========================================================================
    #    #==========================================================================
    #    #Arduino based analysis
    #    #=========================================================================
    alpaca=read_data(data_path,file_name_alpaca)
    alpaca_calib=apply_correction(alpaca)
    unit_time,p_levels,Temp_pint,RH_pint,Theta= data_interpolation_p_t(alpaca_calib,ref,p_intv_no,instrument_spef)
    p_mid_levels,Temp_diff,Theta_diff,RH_diff=get_gradients(unit_time,p_levels,Temp_pint,Theta,RH_pint)
    z_BL_q, p_BL_q = boundary_layer_height(RH_pint, Temp_pint, p_levels, 'specific_humidity')
    z_BL_rh,p_BL_rh=boundary_layer_height(RH_pint, Temp_pint, p_levels, 'relative_humidity')
    z_BL_theta,p_BL_theta=boundary_layer_height(RH_pint,Temp_pint,p_levels,'potential_temperature')
    z_BL_theta_e,p_BL_theta_e=boundary_layer_height(RH_pint,Temp_pint,p_levels,'pseudopotential_temperature')
    ceilo_path="//192.168.206.173/Wettermast/Daten/Export/"
    
    #month
    #day
    
    a="CL_BLHGTA_2018"+month+day+"0000-2018"+month+day+"2359.csv"
    b="CL_BLHGTB_2018"+month+day+"0000-2018"+month+day+"2359.csv"
    c="CL_BLHGTC_2018"+month+day+"0000-2018"+month+day+"2359.csv"
    if day=="05":
        a="CL_BLHGTA_2018"+month+day+"0000-2018"+month+day+"1800.csv"
        b="CL_BLHGTB_2018"+month+day+"0000-2018"+month+day+"1800.csv"
        c="CL_BLHGTC_2018"+month+day+"0000-2018"+month+day+"1800.csv"
    
    file_name=[ceilo_path+a,ceilo_path+b,ceilo_path+c]
    ceilo_bl=np.zeros([1081,4])
    j=0
    #time_vector= np.arange(datetime(2018,9,4), datetime(2018,9,5), timedelta(minutes=1)).astype(datetime)
    first_date=datetime.datetime(2018,int(month),int(day),0,0)
    time = first_date + np.arange(1081) * datetime.timedelta(minutes=1)
    ceilo_bl[:,0]=date2num(time)
    for i in file_name:
        data=np.genfromtxt(i)
        ceilo_bl[:,j+1]=data
        j+=1
    ceilo_new=ceilo_bl[np.where(np.logical_and(ceilo_bl[:,0] > unit_time[1], ceilo_bl[:,0] <= unit_time[-1:]))]
    #keys=list(alpaca)
    #key_idx= np.asarray(keys)        #ard_number=np.array([1,2,3,4,5,6,7,8,9,10,11])
    ceilo_tint=np.zeros([len(unit_time),4])
    ceilo_tint[:,0]=unit_time   
    for j in range(1,4): # 0 Time, 1 Temp, 2 RH, 3 
                    ceilo_tint[:,j]= interp1d(ceilo_new[:,0],ceilo_new[:,j],axis=0,fill_value='extrapolate')(unit_time)
                    print(file_name[j-1][45:51], " Ceilometer height; time interpolated")
    fig_name="BL_height"+file_name_alpaca[:-4]+".png"
    fig_title="Date "+file_name_alpaca[6:8]+"."+file_name_alpaca[4:6]+"."+file_name_alpaca[0:4]+" ,Start Time: "+file_name_alpaca[8:10]+":"+file_name_alpaca[10:12]+":"+file_name_alpaca[12:14] 
    print('Plotting Boundary layer height')
    fig= plt.figure(figsize=(20,10))
    ax= fig.add_subplot(212)
    plt.rcParams.update({'font.size': 12})  
    ax.plot(num2date(unit_time), z_BL_rh, label='Relative Humidity')
    ax.set_xlabel('Time')
    ax.set_ylabel('Boundary Layer Height [m]')
    ax.set_ylim([0,1500])
    ax.set_xticks(ax.get_xticks()[::])
    ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
    ax.plot(num2date(unit_time), z_BL_q, label='Specific Humidity')
    ax.plot(num2date(unit_time), z_BL_theta, label='Potential Temperature')
    ax.plot(num2date(unit_time), z_BL_theta_e, label='Pseudopotential Temperature')
    ax.plot(num2date(unit_time),ceilo_tint[:,1], label="Ceilometer Result")
    ax.legend()
    #ax.set_xlim(datetime.datetime(2018, 8, 29, 7, 50), datetime.datetime(2018, 8, 29, 14, 50))
    #ax.set_xlim(datetime.datetime(2018, 9, 3, 13, 40), datetime.datetime(2018, 9, 3, 16, 30))
    #ax[1].set_xlabel('Time')
    #ax[1].set_ylabel('Boundary Layer Height [m]')
    #ax[1].set_xticks(ax[0].get_xticks()[::])
    #ax[1].xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
    fig.savefig(fig_name, dpi=500,bbox_inches='tight')
    fig.savefig(plot_path+fig_name,dpi=500,bbox_inches="tight")
    print('BL_ALPACA_CEILO plotted and stored on server')
    plt.close()
    return ceilo_new, ceilo_tint;

ceilo_new,ceilo_tint=compare_alpaca_bl_to_ceilometer("05","09")
#    