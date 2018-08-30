# -*- coding: utf-8 -*-
"""
Collection of functions to plot ALPACA data. 
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


#############################################
##Example code to run profile_plot_series
filename="20180829062417_Grenzschichtentwicklung.npy"
ref=0                                                               
p_intv_no=20      
#############################################

def profile_plot_series(filename,ref,p_intv_no):
    """
    Contourf for time series of vertical profiles of temperature/pot. temperatur and humidty for the whole npy. file

    Parameters: 
        filename (str)  :       name of data file
        ref             :       Reference Alpaca for time period
        p_intv_no       :       Number of Pressure levels between boundaries
        fig_name        :       #Name of figure, using date information
    """
    c_p=1005 #J/(kg*K)
    R_l=287  #J/(kg*K)
    
    #Figure name and Plot Title#
    data_path="//192.168.206.173/lex2018/profil/Daten/"
    fig_name=filename[:-4]+"profile_complete.png"
    fig_title="Date "+filename[6:8]+"."+filename[4:6]+"."+filename[0:4]+" ,Start Time: "+filename[8:10]+":"+filename[10:12]+":"+filename[12:14] 
    
    ###########################################################################
    ##Processing of data
    ###########################################################################
    data=np.load(data_path+filename)
    keys=list(data)
    arduino={}
    unit_time=data[keys[ref]][1:,0]
    key_idx= np.asarray(keys)        #ard_number=np.array([1,2,3,4,5,6,7,8,9,10,11])
    interp_data=np.zeros([len(key_idx),4,len(unit_time)])
    
    for i in range(0,len(keys)):
        for j in range(0,4): # 0 Time, 1 Temp, 2 RH, 3 
            arduino[keys[i]]=np.asarray(data[keys[i]])
            interp_data[i,j,:]= interp1d(arduino[keys[i]][1::,0],arduino[keys[i]][1::,j],axis=0,fill_value='extrapolate')(unit_time)
    print("Data time interpolated")
    
    p_min=interp_data[:,3,:].min()
    p_max=interp_data[:,3,:].max()
    p_levels=np.linspace(p_min,p_max,p_intv_no)
    pres_interp=np.zeros([len(p_levels),4,len(unit_time)])
    for t in range(0,len(unit_time)):
        for j in range(0,3):
                pres_interp[:,j,t]=interp1d(interp_data[::,3,t],interp_data[::,j,t],axis=0,fill_value=np.nan,bounds_error=False)(p_levels)
    print("Data p-interpolated")
    Temp_pint=pres_interp[:,1,:]
    RH_pint=pres_interp[:,2,:]
    
    #Pot. Temperatur
    Theta = np.empty((p_intv_no,len(unit_time),))
    Theta.fill(np.nan)
    for t in range(0,len(unit_time)):
        for p in range(0,len(p_levels)):
            Theta[p,t]=(Temp_pint[p,t]+273.15)*(1000/p_levels[p])**(R_l/c_p)
            
    ###########################################################################
    ##Plot data
    ###########################################################################
    print("Plotting...")
    fig= plt.figure(figsize=(30,15))
    matplotlib.rcParams.update({'font.size': 14})
    
    levels_t = np.arange(12, 23, 0.5)
    levels_theta = np.arange(15, 24, 0.5)
    #######################################
    #Subplot1: Temperatur
    ax1=fig.add_subplot(311)
    X,Y = np.meshgrid(unit_time,p_levels)
    C= ax1.contourf(X,Y,Temp_pint,levels_t, cmap=plt.get_cmap("hot_r", len(levels_t)-1))
    cb=plt.colorbar(C)
    cb.set_label('Temperatur in $^\circ$C',fontsize=16)
    #
    ax1.set_xticks(ax1.get_xticks()[::])
    ax1.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
    ax1.set_xlim([unit_time[0],date2num(datetime.datetime(2018, 8, 29, 14, 56))])
    #ax1.set_xlabel('Local Time')
    ax1.set_ylabel('Pressure in hPa')
    ax1.grid()
    #Plot Title
    fig_title="Date "+filename[6:8]+"."+filename[4:6]+"."+filename[0:4]+" ,Start Time: "+filename[8:10]+":"+filename[10:12]+":"+filename[12:14] 
    plt.title(fig_title, fontsize=16)
    #extra settings for axes and ticks
    plt.setp(plt.gca().xaxis.get_majorticklabels(),'rotation', 30)
    plt.gca().invert_yaxis()
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                wspace=None, hspace=0.3)# for space between the subplots  
    
    
    ###################################### 
    #Subplot2 pot. Temperatur
    ax2=fig.add_subplot(312)
    X,Y = np.meshgrid(unit_time,p_levels)
    C2= ax2.contourf(X,Y,Theta-273.15, levels_theta, cmap=plt.get_cmap("hot_r", len(levels_theta)-1))
    cb=plt.colorbar(C2)
    cb.set_label('$\Theta$ in $^\circ$C',fontsize=16)
    
    ax2.set_xticks(ax2.get_xticks()[::])
    ax2.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
    ax2.set_xlim([unit_time[0],date2num(datetime.datetime(2018, 8, 29, 14, 56))])
    ax2.grid()
    #ax2.set_xlabel('Local Time')
    ax2.set_ylabel('Pressure in hPa')
    plt.gca().invert_yaxis()
    plt.setp(plt.gca().xaxis.get_majorticklabels(),'rotation', 30)
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                wspace=None, hspace=0.3)   
    
    ######################################
    #Subplot3 Relative Humidity
    ax3=fig.add_subplot(313)
    C3= ax3.contourf(X,Y,RH_pint,cmap=plt.get_cmap("viridis_r"))
    cb=plt.colorbar(C3)
    cb.set_label('RH in %',fontsize=16)
    ax3.set_xticks(ax3.get_xticks()[::])
    ax3.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
    ax3.set_xlim([unit_time[0], date2num(datetime.datetime(2018, 8, 29, 14, 56))])
    #ax3.set_xlabel('Local Time')
    ax3.set_ylabel('Pressure in hPa')
    ax3.grid()   
    plt.gca().invert_yaxis()
    plt.setp(plt.gca().xaxis.get_majorticklabels(),'rotation', 30)
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                wspace=None, hspace=0.3)
    fig.savefig(fig_name, dpi=500,bbox_inches='tight')
    server_path="//192.168.206.173//lex2018/profil/Plots/"
    fig.savefig(server_path+fig_name,dpi=500,bbox_inches="tight")
    
    print("Plotted and stored on server")
    plt.close()
    return Theta,p_levels,Temp_pint,unit_time;
    ###########################################################################
    ###########################################################################

            



def profilplot(path, filename, time_start, time_end):
    """
    Plots vertica profiles of temperature and humidty for a given time period.
    
    Parameters:
        path (str): path to data file
        filename (str): name of data file
        time_start (datetime.datetime(yyyy, mm, dd, HH, MM, SS)): start time of
            time period
        time_end (datetime.datetime(yyyy, mm, dd, HH, MM, SS)): end time of 
            time period
    """
    plt.rcParams.update({'font.size': 14})
    
    data = np.load(join(path, filename))
    
    temp = {}
    hum = {}
    pres = {}
    for alpaca in data:
        temp[alpaca] = data[alpaca][np.logical_and(data[alpaca][:, 0] >= date2num(time_start), data[alpaca][:, 0] <= date2num(time_end)), 1]
        hum[alpaca] = data[alpaca][np.logical_and(data[alpaca][:, 0] >= date2num(time_start), data[alpaca][:, 0] <= date2num(time_end)), 2]
        pres[alpaca] = data[alpaca][np.logical_and(data[alpaca][:, 0] >= date2num(time_start), data[alpaca][:, 0] <= date2num(time_end)), 3]
        if len(temp[alpaca]) == 0:
            temp[alpaca] = np.array([data[alpaca][data[alpaca][:, 0] >= date2num(time_start), 1][0]])
            hum[alpaca] = np.array([data[alpaca][data[alpaca][:, 0] >= date2num(time_start), 2][0]])
            pres[alpaca] = np.array([data[alpaca][data[alpaca][:, 0] >= date2num(time_start), 3][0]])
        print('Arduino {}: Number of averaged timesteps: {}'.format(alpaca, len(temp[alpaca])))
        temp[alpaca] = np.mean(temp[alpaca])
        hum[alpaca] = np.mean(hum[alpaca])
        pres[alpaca] = np.mean(pres[alpaca])
    
    fig, ax = plt.subplots(1, 2, figsize=(8, 8))
    
    ax[0].plot(temp.values(), pres.values(), 'x', mew=2)
    ax[0].set_xlabel('Temperature [K]')
    ax[0].set_ylabel('Pressure [hPa]')
    ax[1].plot(hum.values(), pres.values(), 'x', mew=2)
    ax[1].set_xlabel('Humidity [%]')
    #ax[1].set_ylabel('Pressure [hPa]')
    
    plt.tight_layout()



#==============================================================================
#i=0
#while True:
#     time.sleep(1)
#     i += 1
#     print(i)
#     if np.mod(i,60) == 0 :
         #run function profile_plot_series
#         try:    
#Theta,p_levels,Temp_pint, unit_time = profile_plot_series(filename,ref,p_intv_no)
#         except:
#             print('NOPE...')
#==============================================================================
    
def plot_timeseries(path, filename, start_time=None, end_time=None, t_range=None,
                    h_range=None, p_range=None):
    """ Plots a timeseries of ALPACA data for the time period between start_time
    and end_time. If no start end end times are given, the whole timeseries in
    the file is plotted. Plot limits for temperature, humidity and pressure can
    be specified optionally.
    
    Parameters:
        path (str): path to data file
        filename (str): name of data file
        start_time (datetime.datetime object): start time of time series
        end_time (datetime.datetime object): end time of time series
        t_range (list with 2 elements): limits for temperature plot
        h_range (list with 2 elements): limits for humidity plot
        p_range (list with 2 elements): limits for pressure plot
    """

    #data = np.load(path + filename)
    data = apply_correction(path, filename)
    
    temp = {}
    hum = {}
    pres = {}
    t = {}
    numarduinos = len(list(data))
    
    halfslave = int(11/2)+1
    jet = plt.get_cmap('gist_rainbow',int(halfslave))
    print(halfslave)
    
    for i in range(1, numarduinos + 1):
        temp[i] = data[i][1:, 1]
        hum[i] = data[i][1:, 2]
        pres[i] = data[i][1:, 3]
        t[i] = data[i][1:, 0]
    
    plt.rcParams.update({'font.size': 14})    
    fig, ax = plt.subplots(3, 1, figsize=(15, 10))
    for i in range(1, numarduinos + 1):
        cindex = np.mod(i-1,halfslave)
        print(cindex)
        if i+1 > halfslave:
            stylus = '--'
        else:
            stylus = '-'
        
        ax[0].plot(num2date(t[i]), temp[i], color=jet(cindex), linestyle=stylus, label=i)
        ax[0].set_xlabel('Time')
        ax[0].set_ylabel('Temperature [°C]')
        ax[1].plot(num2date(t[i]), hum[i], color=jet(cindex), linestyle=stylus, label=i)
        ax[1].set_xlabel('Time')
        ax[1].set_ylabel('Humidity [%]')
        ax[2].plot(num2date(t[i]), pres[i], color=jet(cindex), linestyle=stylus, label=i)
        ax[2].set_xlabel('Time')
        ax[2].set_ylabel('Pressure [hPa]')
    
    ax[2].legend(loc='upper center', bbox_to_anchor=(0.8, -0.2),
          fancybox=True, shadow=True, ncol=5)

    if start_time is not None:
        start_lim = start_time
    else:
        start_lim = t[1][0]
    if end_time is not None:
        end_lim = end_time
    else:
        end_lim = t[1][-1]
        
    ax[0].set_xlim(start_lim, end_lim)
    ax[1].set_xlim(start_lim, end_lim)
    ax[2].set_xlim(start_lim, end_lim)
    
    if t_range is not None:
        ax[0].set_ylim(t_range[0], t_range[1])
    if h_range is not None:
        ax[1].set_ylim(h_range[0], h_range[1])
    if p_range is not None:
        ax[2].set_ylim(p_range[0], p_range[1])

    plt.tight_layout()

def altitude(pressure, temperature):
    """ Calculates altitude fromm pressure and temperature.
    
    Parameters:
        pressure (array): vertical pressure profile 
        temperature (array): vertical temperature profile
    """
    
    # constants
    R = 287.058
    g = 9.81
    z = np.zeros(len(pressure))
    z_interv = np.zeros(len(pressure))
    z0 = 7.0

    for lev in range(0, len(pressure)-1):
        z_interv[lev+1] = np.log(pressure[lev+1] / pressure[lev]) * -(R * (temperature[lev] + temperature[lev+1]) / 2 / g)
        
        z[lev+1] = np.sum(z_interv)
        
    return z + z0

def apply_correction(path, filename):
    """ Applies temperature and himidity correction to ALPACA raw data and 
    returns a dictionary with the same structure as in the raw data, but 
    with the corrected values. 
    """
    
    data = np.load(path + filename)
    arduinos = data.keys()
    
    temp_correction = {1: 0.09, 2: 0.10, 3: -0.02, 4: -0.23, 5: -0.20,
                       6: 0.05, 7: 0.14, 8: 0.11, 9: -0.10, 10: 0.11,
                       11: -0.09}
    
    humidity_correction = {1: -0.10, 2: 0.34, 3: -0.03, 4: 0.17, 5: 0.48,
                       6: -0.14, 7: -2.09, 8: 1.07, 9: -0.60, 10: -0.30,
                       11: 2.00}
    
    for i in arduinos:
        # temperature
        data[i][1:, 1] = data[i][1:, 1] + temp_correction[i]
        # humidity
        data[i][1:, 2] = data[i][1:, 2] + humidity_correction[i]
        
    return data
