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
from processing_functions import calc_virt_pot,calc_bulk_richardson
from processing_functions import smooth_variable
from plot_functions import profile_plot_series
from plot_functions import alt_time_plot
from plot_functions import plot_timeseries
from plot_functions import gradient_profile_plot_series
from plot_functions import plot_boundary_layer_height
from matplotlib import dates


def compare_alpaca_bl_to_ceilometer(day,month):

    instrument_spef=0                                       #leave it 0!)
    data_path="C:/Users/Henning/Desktop/LEX_Netzwerk/profil/Daten/"
    date_alpaca=["20180829062417","20180831105131","20180901095651","20180903132225","20180904124938","20180905094034"]
    date=["29","31","01","03","04","05"]
    l = [date.index(i) for i in date if day in i]
    idx=int(l[0])+1
    if day=="03":
      file_name_alpaca=date_alpaca[l[0]]+"_Grenzschichtentwicklung"+str(idx)+"_2.npy"  
    else:
      file_name_alpaca=date_alpaca[l[0]]+"_Grenzschichtentwicklung"+str(idx)+".npy"  
    file=data_path+file_name_alpaca
    ref=0                                                               
    p_intv_no=20 
    z_intv_no=p_intv_no                                           # number of pressure levels to interpolate
    plot_path="C:/Users/Henning/Desktop/LEX_Netzwerk/profil/Plots/Liveplots/"       
        
    #==========================================================================
    #==========================================================================
    #Arduino based analysis
    #use of functions from processing_functions.py
    #=========================================================================
    alpaca=read_data(data_path,file_name_alpaca)
    alpaca_calib=apply_correction(alpaca)
    unit_time,p_levels,Temp_pint,RH_pint,Theta= data_interpolation_p_t(alpaca_calib,ref,p_intv_no,instrument_spef)
    p_mid_levels,Temp_diff,Theta_diff,RH_diff=get_gradients(unit_time,p_levels,Temp_pint,Theta,RH_pint)
    z_BL_q, p_BL_q = boundary_layer_height(RH_pint, Temp_pint, p_levels, 'specific_humidity')
    z_BL_rh,p_BL_rh=boundary_layer_height(RH_pint, Temp_pint, p_levels, 'relative_humidity')
    z_BL_theta,p_BL_theta=boundary_layer_height(RH_pint,Temp_pint,p_levels,'potential_temperature')
    z_BL_theta_e,p_BL_theta_e=boundary_layer_height(RH_pint,Temp_pint,p_levels,'pseudopotential_temperature')
    ceilo_path="C:/Users/Henning/Desktop/LEX_Netzwerk/Export/"
                
    a="CL_BLHGTA_2018"+month+day+"0000-2018"+month+day+"2359.csv"
    b="CL_BLHGTB_2018"+month+day+"0000-2018"+month+day+"2359.csv"
    c="CL_BLHGTC_2018"+month+day+"0000-2018"+month+day+"2359.csv"
    if day=="05":
        a="CL_BLHGTA_2018"+month+day+"0000-2018"+month+day+"1800.csv"
        b="CL_BLHGTB_2018"+month+day+"0000-2018"+month+day+"1800.csv"
        c="CL_BLHGTC_2018"+month+day+"0000-2018"+month+day+"1800.csv"
        
    file_name=[ceilo_path+a,ceilo_path+b,ceilo_path+c]
    if day == "05":
        ceilo_bl=np.zeros([1081,4])
        j=0
        first_date=datetime.datetime(2018,int(month),int(day),0,0)
        time = first_date + np.arange(1081) * datetime.timedelta(minutes=1)
    else:
        ceilo_bl=np.zeros([1440,4])
        j=0
        first_date=datetime.datetime(2018,int(month),int(day),0,0)
        time = first_date + np.arange(1440) * datetime.timedelta(minutes=1)
        
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
    
    cosmo_ceilo_time,cosmo_all_time,cosmo_data,c_potT_bnd,c_pseudoPotT_bnd,c_relH_bnd,c_QV_bnd,ceil_values_for_cosmo,=process_cosmo_data_for_ceilo_meter(day,month,ceilo_new)
    fig_name="BL_height_1m_avg"+file_name_alpaca[:-4]+".png"
    fig_title="Date "+file_name_alpaca[6:8]+"."+file_name_alpaca[4:6]+"."+file_name_alpaca[0:4]+" ,Start Time: "+file_name_alpaca[8:10]+":"+file_name_alpaca[10:12]+":"+file_name_alpaca[12:14] 
    print('Plotting Boundary layer height')
    fig= plt.figure(figsize=(20,10))
    ax= fig.add_subplot(212)
    plt.rcParams.update({'font.size': 12})  
    ax.plot(num2date(ceilo_new[:,0]), z_bl_rh, label='Relative Feuchte')
    ax.set_xlabel('Uhrzeit [MESZ]')
    ax.set_ylabel('Grenzschicht Höhe [m]')
    ax.set_ylim([0,1500])
    ax.set_xticks(ax.get_xticks()[::])
    ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
    ax.plot(num2date(ceilo_new[:,0]), z_bl_q, label='Spezifische Feuchte')
    ax.plot(num2date(ceilo_new[:,0]), z_bl_theta, label='Pot. Temperatur')
    ax.plot(num2date(ceilo_new[:,0]), z_bl_theta_e, label='Pseudopot. Temperatur')
    ax.plot(num2date(ceilo_new[:,0]),ceilo_new[:,1], color="black",label="Ceilometer")
    ax.plot(cosmo_ceilo_time,c_relH_bnd,'b+',label='RH (Cosmo)',alpha=0.8)
    ax.plot(cosmo_ceilo_time,c_QV_bnd,'o',color='orange',label='Spez. Feuchte (Cosmo)',alpha=0.8)
    ax.plot(cosmo_ceilo_time,c_potT_bnd,'g*',label='Pot. T. (Cosmo)',alpha=0.8)
    ax.plot(cosmo_ceilo_time,c_pseudoPotT_bnd,'rv',label='Pseudopot. T. (Cosmo)',alpha=1.0)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),fancybox=True, ncol=5)
    ax.grid()
    fig.savefig(plot_path+fig_name,dpi=500,bbox_inches="tight")
       
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

####### Process Cosmo data for comparison######################################
###############################################################################
###############################################################################
def process_cosmo_data_for_ceilo_meter(day,month,ceilo_new):
    cosmo_data=cosmo.cosmoData("C:/Users/Henning/Desktop/LEX_Netzwerk/profil/Daten/Cosmo/cd2_feh_2018"+month+day+"00.nc")
    cosmo_first_time=datetime.datetime(2018,int(month),int(day),2,0)
    cosmo_all_time = cosmo_first_time + np.arange(28) * datetime.timedelta(minutes=60)
    cosmo_ceilo_time=cosmo_all_time[np.where(np.logical_and(date2num(cosmo_all_time) >= ceilo_new[0,0], date2num(cosmo_all_time) <= ceilo_new[-1:,0]))]
    c_potT_bnd,c_pseudoPotT_bnd,c_relH_bnd,c_QV_bnd=cosmo_data.get_bnd_layers()
    c_potT_bnd=c_potT_bnd[np.where(np.logical_and(date2num(cosmo_all_time) >= ceilo_new[0,0], date2num(cosmo_all_time) <= ceilo_new[-1:,0]))]
    c_pseudoPotT_bnd=c_pseudoPotT_bnd[np.where(np.logical_and(date2num(cosmo_all_time) >= ceilo_new[0,0], date2num(cosmo_all_time) <= ceilo_new[-1:,0]))]
    c_relH_bnd=c_relH_bnd[np.where(np.logical_and(date2num(cosmo_all_time) >= ceilo_new[0,0], date2num(cosmo_all_time) <= ceilo_new[-1:,0]))]
    c_QV_bnd=c_QV_bnd[np.where(np.logical_and(date2num(cosmo_all_time) >= ceilo_new[0,0], date2num(cosmo_all_time) <= ceilo_new[-1:,0]))]
    ceil_values_for_cosmo=np.zeros([len(cosmo_ceilo_time)])
    for i in range(len(cosmo_ceilo_time)):
        ceil_values_for_cosmo[i]=ceilo_new[np.where(ceilo_new[:,0]==date2num(cosmo_ceilo_time[i])),1]
    return cosmo_ceilo_time,cosmo_all_time,cosmo_data,c_potT_bnd,c_pseudoPotT_bnd,c_relH_bnd,c_QV_bnd,ceil_values_for_cosmo,;
###############################################################################
###############################################################################
def process_cosmo_for_Ri_bulk(cosmo_data,ceilo_new,cosmo_all_time):
    u_cosmo=cosmo_data.U[:,cosmo_data.maxlevel:-1,11,10]
    v_cosmo=cosmo_data.V[:,cosmo_data.maxlevel:-1,11,10]
    T_cosmo=cosmo_data.T[:,cosmo_data.maxlevel:-1,11,10]
    RH_cosmo=cosmo_data.RH[:,cosmo_data.maxlevel:-1,11,10]
    P_cosmo=cosmo_data.P[:,cosmo_data.maxlevel:-1,11,10]
    heights_cosmo=cosmo_data.heights[:]
    heights_cosmo=np.transpose(heights_cosmo)
    u_cosmo=u_cosmo[np.where(np.logical_and(date2num(cosmo_all_time) >= ceilo_new[0,0], date2num(cosmo_all_time) <= ceilo_new[-1:,0])),:]
    v_cosmo=v_cosmo[np.where(np.logical_and(date2num(cosmo_all_time) >= ceilo_new[0,0], date2num(cosmo_all_time) <= ceilo_new[-1:,0])),:]
    T_cosmo=T_cosmo[np.where(np.logical_and(date2num(cosmo_all_time) >= ceilo_new[0,0], date2num(cosmo_all_time) <= ceilo_new[-1:,0])),:]
    RH_cosmo=RH_cosmo[np.where(np.logical_and(date2num(cosmo_all_time) >= ceilo_new[0,0], date2num(cosmo_all_time) <= ceilo_new[-1:,0])),:]
    P_cosmo=P_cosmo[np.where(np.logical_and(date2num(cosmo_all_time) >= ceilo_new[0,0], date2num(cosmo_all_time) <= ceilo_new[-1:,0])),:]
    heights_cosmo=np.tile(heights_cosmo,(u_cosmo.shape[1],1))
    return u_cosmo,v_cosmo,T_cosmo,RH_cosmo,P_cosmo,heights_cosmo
###############################################################################
###############################################################################
####### Scatter plot of ALPACA vs. sonde#######################################
def scatterplot_bl_alpaca_ceilometer(day,month,z_bl_rh,z_bl_q,z_bl_theta,z_bl_theta_e,file_name_alpaca):
    cosmo_ceilo_time,cosmo_all_time,cosmo_data,c_potT_bnd,c_pseudoPotT_bnd,c_relH_bnd,c_QV_bnd,ceil_values_for_cosmo=process_cosmo_data_for_ceilo_meter(day,month,ceilo_new)
    plot_path="C:/Users/Henning/Desktop/LEX_Netzwerk/profil/Plots/Liveplots/"     
    fig_name=plot_path+"BL_height_Scatter"+file_name_alpaca[:-4]+".png"
    fig= plt.figure(figsize=(10,6))
    matplotlib.rcParams.update({'font.size': 14})
    ax=fig.add_subplot(111)
    ax.plot([min(ceilo_new[:,1])-50, max(ceilo_new[:,1])+50],[min(ceilo_new[:,1])-50, max(ceilo_new[:,1])+50],color='black')
    ax.scatter(z_bl_rh,ceilo_bl_rh,marker='+',color = 'b',label='Relative Feuchte')
    ax.scatter(z_bl_q,ceilo_bl_q,marker='o',color='orange',label='Spezifische Feuchte')
    ax.scatter(z_bl_theta,ceilo_bl_theta,marker='*',color='green',label='Pot. Temperatur')
    ax.scatter(z_bl_theta_e,ceilo_bl_theta_e,marker='v',color='red',label='Pseudopot. Temperatur')
    ##cosmo part
    ax.scatter(c_relH_bnd,ceil_values_for_cosmo,marker='+',color = 'k',label="RH (Cosmo)")
    ax.scatter(c_QV_bnd,ceil_values_for_cosmo,marker='o',color='k',label="Spez. Feuchte (Cosmo)")
    ax.scatter(c_potT_bnd,ceil_values_for_cosmo,marker='*',color='k',label="Pot. T (Cosmo)")
    ax.scatter(c_pseudoPotT_bnd,ceil_values_for_cosmo,marker='v',color='k',label="Pseudopot. T. (Cosmo)")
    ax.set_xlim([min(ceilo_new[:,1])-50, max(ceilo_new[:,1])+50])
    ax.set_xlabel('BL Höhe Arduinos/Cosmo [m]')
    ax.set_ylabel('BL Höhe Ceilometer [m] ')
    ax.set_ylim([min(ceilo_new[:,1])-50, max(ceilo_new[:,1])+50])
    ax.grid(linestyle='--',alpha=0.5)
    ax.legend(loc='center right', bbox_to_anchor=(1.375, 0.5),fontsize=12)
    #fig.suptitle('Ceilometer-ALPACA Vergleich')
    fig.savefig(fig_name,dpi=500,bbox_inches='tight')
    print("Scatterplot saved and stored on server")
    return;
###############################################################################
###############################################################################
#End of functions
###############################################################################
#define the desired date for analyse
day="29"
month="08"
###############################################################################
#Use the functions:
ceilo_new, z_BL_q, z_BL_rh, z_BL_theta, z_BL_theta_e,file_name_alpaca=compare_alpaca_bl_to_ceilometer(day,month)
cosmo_ceilo_time,cosmo_all_time,cosmo_data,c_potT_bnd,c_pseudoPotT_bnd,c_relH_bnd,c_QV_bnd,ceil_values_for_cosmo=process_cosmo_data_for_ceilo_meter(day,month,ceilo_new) 

#calculate the RI-bulk number:
u_cosmo,v_cosmo,T_cosmo,RH_cosmo,P_cosmo,heights_cosmo=process_cosmo_for_Ri_bulk(cosmo_data,ceilo_new,cosmo_all_time)
virtpot_temp_cosmo=calc_virt_pot(RH_cosmo, T_cosmo-273.15, P_cosmo/100)
ws_cosmo=np.sqrt(u_cosmo**2+v_cosmo**2)
Ri=calc_bulk_richardson(virtpot_temp_cosmo[0,:,0:20],ws_cosmo[0,:,0:20], heights_cosmo)
z_bl_Ri = np.zeros((Ri.shape[0]))
for i in range(Ri.shape[0]):
    z_bl_Ri[i] = interp1d(Ri[i,:], heights_cosmo[i,:], bounds_error=False, fill_value=np.nan)(0.2)

#statistics
bias_rh,rmse_rh,r_bl_rh,ceilo_bl_rh,z_bl_rh=calc_bias_rms_bl(z_BL_rh,ceilo_new)
bias_q,rmse_q,r_bl_q,ceilo_bl_q,z_bl_q=calc_bias_rms_bl(z_BL_q,ceilo_new)
bias_theta,rmse_theta,r_bl_theta,ceilo_bl_theta,z_bl_theta=calc_bias_rms_bl(z_BL_theta,ceilo_new)
bias_theta_e,rmse_theta_e,r_bl_theta_e,ceilo_bl_theta_e,z_bl_theta_e=calc_bias_rms_bl(z_BL_theta_e,ceilo_new) 
scatterplot_bl_alpaca_ceilometer(day,month,z_bl_rh,z_bl_q,z_bl_theta,z_bl_theta_e,file_name_alpaca)
