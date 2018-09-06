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
import cosmo
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
    #day="05"
    #month="09"
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
        
        #Interpolate Ceilometer on Alpaca Resolution
     #   ceilo_tint=np.zeros([len(unit_time),4])
      #  ceilo_tint[:,0]=unit_time   
       # for j in range(1,4): # 0 Time, 1 Temp, 2 RH, 3 
        #                ceilo_tint[:,j]= interp1d(ceilo_new[:,0],ceilo_new[:,j],axis=0,fill_value='extrapolate')(unit_time)
         #               print(file_name[j-1][45:51], " Ceilometer height; time interpolated")
    z_bl_rh=np.zeros(len(ceilo_new[:,0]))
    z_bl_q=np.zeros(len(ceilo_new[:,0]))
    z_bl_theta=np.zeros(len(ceilo_new[:,0]))
    z_bl_theta_e=np.zeros(len(ceilo_new[:,0]))
         
    for i in range(len(ceilo_new)-1):
         alpaca_bl_rh     = z_BL_rh[np.where(np.logical_and(unit_time >= ceilo_new[i,0], unit_time <= ceilo_new[i+1,0]))]
         alpaca_bl_q      = z_BL_q[np.where(np.logical_and(unit_time >= ceilo_new[i,0], unit_time <= ceilo_new[i+1,0]))]
         alpaca_bl_theta  = z_BL_theta[np.where(np.logical_and(unit_time >= ceilo_new[i,0], unit_time <= ceilo_new[i+1,0]))]
         alpaca_bl_theta_e= z_BL_theta_e[np.where(np.logical_and(unit_time >= ceilo_new[i,0], unit_time <= ceilo_new[i+1,0]))]
         z_bl_rh[i]       = np.mean(alpaca_bl_rh)
         z_bl_q[i]        = np.mean(alpaca_bl_q)
         z_bl_theta[i]    = np.mean(alpaca_bl_theta)
         z_bl_theta_e[i]  = np.mean(alpaca_bl_theta_e)
    
    
    fig_name="BL_height_1m_avg"+file_name_alpaca[:-4]+".png"
    fig_title="Date "+file_name_alpaca[6:8]+"."+file_name_alpaca[4:6]+"."+file_name_alpaca[0:4]+" ,Start Time: "+file_name_alpaca[8:10]+":"+file_name_alpaca[10:12]+":"+file_name_alpaca[12:14] 
    print('Plotting Boundary layer height')
    fig= plt.figure(figsize=(20,10))
    ax= fig.add_subplot(212)
    plt.rcParams.update({'font.size': 12})  
    ax.plot(num2date(ceilo_new[:,0]), z_bl_rh, label='Relative Humidity')
    ax.set_xlabel('Time')
    ax.set_ylabel('Boundary Layer Height [m]')
    ax.set_ylim([0,1500])
    ax.set_xticks(ax.get_xticks()[::])
    ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
    ax.plot(num2date(ceilo_new[:,0]), z_bl_q, label='Specific Humidity')
    ax.plot(num2date(ceilo_new[:,0]), z_bl_theta, label='Potential Temperature')
    ax.plot(num2date(ceilo_new[:,0]), z_bl_theta_e, label='Pseudopotential Temperature')
    ax.plot(num2date(ceilo_new[:,0]),ceilo_new[:,1], label="Ceilometer Result")
    ax.legend()
    ax.grid()
    fig.savefig(fig_name+".png", dpi=500,bbox_inches='tight')
    fig.savefig(plot_path+fig_name,dpi=500,bbox_inches="tight")
    #fig.savefig(plot_path+fig_name+".svg",bbox_inches="tight")
    
    print('BL_ALPACA_CEILO plotted and stored on server')
    plt.close()
    return ceilo_new, z_bl_q, z_bl_rh, z_bl_theta, z_bl_theta_e,file_name_alpaca;

###############################################################################
#### Calculate BIAS, RMS
###############################################################################
def calc_bias_rms_bl(z_bl,ceilo_bl_all):
    ceilo_bl=ceilo_bl_all[:,1]
    ceilo_bl=ceilo_bl[np.logical_not(np.isnan(z_bl))]
    z_bl = z_bl[np.logical_not(np.isnan(z_bl))]
    bias = np.mean(z_bl-ceilo_bl)
    rmse = np.sqrt(np.mean((z_bl-ceilo_bl)**2))
    r_bl = np.corrcoef(z_bl,ceilo_bl)[0,1]
    print('Boundary Layer Height Statistics:')
    print('BIAS: ',bias)
    print('RMSE: ',rmse)
    print('R: ',r_bl)
    return bias,rmse,r_bl,ceilo_bl,z_bl;

####### Scatter plot of ALPACA vs. sonde#######################################
def scatterplot_bl_alpaca_ceilometer(day,month,z_bl_rh,z_bl_q,z_bl_theta,z_bl_theta_e,file_name_alpaca):
    #date_alpaca=["20180829062417","20180831105131","20180901095651","20180903095623","20180904124938","20180905094034"]
    #file_name_alpaca=date_alpaca[l[0]]+"_Grenzschichtentwicklung"+str(idx)+".npy"
    plot_path="//192.168.206.173//lex2018/profil/Plots/Liveplots/"     
    fig_name=plot_path+"BL_height_Scatter"+file_name_alpaca[:-4]+".png"
    fig= plt.figure(figsize=(10,6))
    matplotlib.rcParams.update({'font.size': 14})
    ax=fig.add_subplot(111)
    ax.plot([min(ceilo_new[:,1])-50, max(ceilo_new[:,1])+50],[min(ceilo_new[:,1])-50, max(ceilo_new[:,1])+50],color='black')
    ax.scatter(z_bl_rh,ceilo_bl_rh,marker='+',color = 'b',label='Relative Feuchte')
    ax.scatter(z_bl_q,ceilo_bl_q,marker='o',color='orange',label='Spezifische Feuchte')
    ax.scatter(z_bl_theta,ceilo_bl_theta,marker='*',color='green',label='Pot. Temperatur')
    ax.scatter(z_bl_theta_e,ceilo_bl_theta_e,marker='v',color='red',label='Pseudopot. Temperatur')
    ax.set_xlim([min(ceilo_new[:,1])-50, max(ceilo_new[:,1])+50])
    ax.set_xlabel('Geschätzte BL Höhe Arduinos in m')
    ax.set_ylabel('Geschätzte BL Höhe Ceilometer in m ')
    ax.set_ylim([min(ceilo_new[:,1])-50, max(ceilo_new[:,1])+50])
    ax.grid(linestyle='--',alpha=0.5)
    ax.legend(loc="best",fontsize=12)
    #fig.suptitle('Ceilometer-ALPACA Vergleich')
    fig.savefig(fig_name,dpi=500,bbox_inches='tight')
    #fig.savefig(fig_name+".svg",bbox_inches='tight')
    print("Scatterplot saved and stored on server")
    return;
###############################################################################
###############################################################################
#Use the functions
day="05"
month="09"
#ceilo_new, z_BL_q, z_BL_rh, z_BL_theta, z_BL_theta_e,file_name_alpaca=compare_alpaca_bl_to_ceilometer(day,month)
#bias_rh,rmse_rh,r_bl_rh,ceilo_bl_rh,z_bl_rh=calc_bias_rms_bl(z_BL_rh,ceilo_new)
#bias_q,rmse_q,r_bl_q,ceilo_bl_q,z_bl_q=calc_bias_rms_bl(z_BL_q,ceilo_new)
#bias_theta,rmse_theta,r_bl_theta,ceilo_bl_theta,z_bl_theta=calc_bias_rms_bl(z_BL_theta,ceilo_new)
#bias_theta_e,rmse_theta_e,r_bl_theta_e,ceilo_bl_theta_e,z_bl_theta_e=calc_bias_rms_bl(z_BL_theta_e,ceilo_new)  
#scatterplot_bl_alpaca_ceilometer("05","09",z_bl_rh,z_bl_q,z_bl_theta,z_bl_theta_e,file_name_alpaca)
###############################################################################
###############################################################################
cosmo_data=cosmo.cosmoData("//192.168.206.173/lex2018/profil/Daten/Cosmo/cd2_feh_2018090500.nc")
potT_bnd,pseudoPotT_bnd,relH_bnd,QV_bnd=cosmo_data.get_bnd_layers()
cosmo_first_time=datetime.datetime(2018,int(month),int(day),2,0)
cosmo_time = cosmo_first_time + np.arange(28) * datetime.timedelta(minutes=60)
#    ceilo_bl[:,0]=date2num(time)