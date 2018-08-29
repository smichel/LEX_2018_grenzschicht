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
    fig_name=filename[:-4]+"profile.png"
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
    fig= plt.figure(figsize=(15,18))
    matplotlib.rcParams.update({'font.size': 14})
    
    #######################################
    #Subplot1: Temperatur
    ax1=fig.add_subplot(311)
    X,Y = np.meshgrid(unit_time,p_levels)
    C= ax1.contourf(X,Y,Temp_pint,cmap=plt.get_cmap("hot_r"))
    cb=plt.colorbar(C)
    cb.set_label('Temperatur in $^\circ$C',fontsize=16)
    ax1.set_xticks(ax1.get_xticks()[::])
    ax1.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
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
    C2= ax2.contourf(X,Y,Theta-273.15,cmap=plt.get_cmap("hot_r"))
    cb=plt.colorbar(C2)
    cb.set_label('$\Theta$ in $^\circ$C',fontsize=16)
    ax2.set_xticks(ax2.get_xticks()[::])
    ax2.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
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
    return Theta,p_levels,Temp_pint;
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



#i=0
#while True:
#    time.sleep(1)
#    i += 1
#    print(i)
#    if np.mod(i,60) == 0 :
#        #run function profile_plot_series
#        try:    
#            Theta,p_levels,Temp_pint = profile_plot_series(filename,ref,p_intv_no)
#        except:
#            print('NOPE...')
    

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
