# -*- coding: utf-8 -*-
"""
Collection of functions to plot ALPACA data. 
"""
import time 
import sys
import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, num2date
import matplotlib
import numpy as np
from os.path import join
from scipy.interpolate import interp1d
from matplotlib import dates
from processing_functions import apply_correction, boundary_layer_height
###############################################################################
###############################################################################
def profile_plot_series(filename,server_path,unit_time,p_levels,Temp_pint,RH_pint,Theta, boundary_layer=False, start_time=None, end_time=None):
    ###########################################################################
    ##Plot data
    fig_name=filename[:-4]+".png"
    fig_title="Date "+filename[6:8]+"."+filename[4:6]+"."+filename[0:4]+" ,Start Time: "+filename[8:10]+":"+filename[10:12]+":"+filename[12:14] 
    ###########################################################################
    print("Plotting...")
    fig= plt.figure(figsize=(30,15))
    matplotlib.rcParams.update({'font.size': 14})
    
    levels_T=np.arange(round(np.nanmin(Temp_pint)),round(np.nanmax(Temp_pint)),(round(np.nanmax(Temp_pint))-round(np.nanmin(Temp_pint)))/20)
    levels_Theta=np.arange(round(np.nanmin(Theta),2),round(np.nanmax(Theta),2),round((np.nanmax(Theta)-np.nanmin(Theta))/20,2)) -273.15
    ###########################################################################
    # calculate boundary layer height
    if boundary_layer:
        z_BL_pseudopot, p_BL_pseudopot = boundary_layer_height(RH_pint, Temp_pint, p_levels, 'pseudopotential_temperature')
        z_BL_pot, p_BL_pot = boundary_layer_height(RH_pint, Temp_pint, p_levels, 'potential_temperature')
        z_BL_hum, p_BL_hum = boundary_layer_height(RH_pint, Temp_pint, p_levels, 'specific_humidity')
        z_BL_relhum, p_BL_relhum = boundary_layer_height(RH_pint, Temp_pint, p_levels, 'relative_humidity')
    
    #time limits:
    if start_time is not None:
        start_lim = start_time
    else:
        start_lim = unit_time[0]
    if end_time is not None:
        end_lim = end_time
    else:
        end_lim = unit_time[-1]
    #Subplot1: Temperatur
    ax1=fig.add_subplot(311)
    X,Y = np.meshgrid(unit_time,p_levels)
    C= ax1.contourf(X,Y,Temp_pint,levels_T,cmap=plt.get_cmap("hot_r", len(levels_T)-1),extend="both")
    if boundary_layer:
        ax1.plot(unit_time, p_BL_relhum, color='C0', label='Relative Humidity')
        ax1.plot(unit_time, p_BL_hum, color='C1', label='Specific Humidity')
        ax1.plot(unit_time, p_BL_pot, color='C2', label='Potential Temperature')
        ax1.plot(unit_time, p_BL_pseudopot, color='C3', label='Pseudopotential Temperature')
        ax1.legend()
    cb=plt.colorbar(C)
    cb.set_label('Temperatur in $^\circ$C',fontsize=16)
    #
    ax1.set_xticks(ax1.get_xticks()[::])
    ax1.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
    ax1.set_xlim([start_lim,end_lim])
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
    C2= ax2.contourf(X,Y,Theta-273.15,levels_Theta,cmap=plt.get_cmap("hot_r",len(levels_Theta)-1),extend="both")
    if boundary_layer:
        ax2.plot(unit_time, p_BL_relhum, color='C0', label='Relative Humidity')
        ax2.plot(unit_time, p_BL_hum, color='C1', label='Specific Humidity')
        ax2.plot(unit_time, p_BL_pot, color='C2', label='Potential Temperature')
        ax2.plot(unit_time, p_BL_pseudopot, color='C3', label='Pseudopotential Temperature')
        
    cb=plt.colorbar(C2)
    cb.set_label('$\Theta$ in $^\circ$C',fontsize=16)
    
    ax2.set_xticks(ax2.get_xticks()[::])
    ax2.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
    ax2.set_xlim(start_lim,end_lim)
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
    if boundary_layer:
        ax3.plot(unit_time, p_BL_relhum, color='C0', label='Relative Humidity')
        ax3.plot(unit_time, p_BL_hum, color='C1', label='Specific Humidity')
        ax3.plot(unit_time, p_BL_pot, color='C2', label='Potential Temperature')
        ax3.plot(unit_time, p_BL_pseudopot, color='C3', label='Pseudopotential Temperature')
    cb=plt.colorbar(C3)
    cb.set_label('RH in %',fontsize=16)
    ax3.set_xticks(ax3.get_xticks()[::])
    ax3.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
    ax3.set_xlim(start_lim,end_lim)
    #ax3.set_xlabel('Local Time')
    ax3.set_ylabel('Pressure in hPa')
    ax3.grid()   
    plt.gca().invert_yaxis()
    plt.setp(plt.gca().xaxis.get_majorticklabels(),'rotation', 30)
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                wspace=None, hspace=0.3)
    fig.savefig(fig_name, dpi=500,bbox_inches='tight')
    fig.savefig(server_path+fig_name,dpi=500,bbox_inches="tight")
    plt.close()
    print("Plotted and stored on server")
    return        

###############################################################################
###############################################################################

def profilplot(data, time_start, time_end):
    """
    Plots vertica profiles of temperature and humidty for a given time period.
    
    Parameters:
        data (dictionary): dictionary with data for all alpacas
        time_start (datetime.datetime(yyyy, mm, dd, HH, MM, SS)): start time of
            time period
        time_end (datetime.datetime(yyyy, mm, dd, HH, MM, SS)): end time of 
            time period
    """
    plt.rcParams.update({'font.size': 14})
    
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


###############################################################################
def gradient_profile_plot_series(filename,server_path,unit_time,Temp_diff,Theta_diff,RH_diff,p_mid_levels):
    ###########################################################################
    ##Plot data
    fig_name="Gradients"+filename[:-4]+".png"
    fig_title="Date "+filename[6:8]+"."+filename[4:6]+"."+filename[0:4]+" ,Start Time: "+filename[8:10]+":"+filename[10:12]+":"+filename[12:14] 
    ###########################################################################
    print("Plotting...")
    fig= plt.figure(figsize=(15,10))
    matplotlib.rcParams.update({'font.size': 14})
    
    #levels_T=np.arange(12,23,0.5)
    #levels_Theta=np.arange(14,25,0.5)
    ###########################################################################
    #Subplot1: Temperatur
    #ax1=fig.add_subplot(311)
    #X,Y = np.meshgrid(unit_time,p_levels)
    #C= ax1.contourf(X,Y,Temp_pint,levels_T,cmap=plt.get_cmap("hot_r", len(levels_T)-1),extend="both")
    #cb=plt.colorbar(C)
    #cb.set_label('Temperatur in $^\circ$C',fontsize=16)
    #
    #ax1.set_xticks(ax1.get_xticks()[::])
    #ax1.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
    #ax1.set_xlim([unit_time[0],unit_time[-1]])
    #ax1.set_xlabel('Local Time')
    #ax1.set_ylabel('Pressure in hPa')
    #ax1.grid()
    #Plot Title
    #fig_title="Date "+filename[6:8]+"."+filename[4:6]+"."+filename[0:4]+" ,Start Time: "+filename[8:10]+":"+filename[10:12]+":"+filename[12:14] 
    #plt.title(fig_title, fontsize=16)
    #extra settings for axes and ticks
    #plt.setp(plt.gca().xaxis.get_majorticklabels(),'rotation', 30)
    #plt.gca().invert_yaxis()
    #plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
    #            wspace=None, hspace=0.3)# for space between the subplots  
    ###################################### 
    #Subplot2 pot. Temperatur
    ax2=fig.add_subplot(211)
    X,Y = np.meshgrid(unit_time,p_mid_levels)
    levels_Theta=np.arange(-0.6,0.7,0.1)
    C2= ax2.contourf(X,Y,Theta_diff,levels_Theta,cmap=plt.get_cmap("coolwarm",len(levels_Theta)-1),extend="both")
    cb=plt.colorbar(C2)
    cb.set_label('$\delta \Theta / \delta$p\n in K/hPa',fontsize=16)
    cb.set_ticks(levels_Theta)
    ax2.set_xticks(ax2.get_xticks()[::])
    ax2.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
    ax2.set_xlim([unit_time[0],unit_time[-1]])
    ax2.grid()
    #ax2.set_xlabel('Local Time')
    ax2.set_ylabel('Pressure in hPa')
    ax2.set_ylim([p_mid_levels[0],p_mid_levels[-1]])
    plt.gca().invert_yaxis()
    plt.setp(plt.gca().xaxis.get_majorticklabels(),'rotation', 30)
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                wspace=None, hspace=0.3)   
    ######################################
    #Subplot3 Relative Humidity
    ax3=fig.add_subplot(212)
    C3= ax3.contourf(X,Y,RH_diff,cmap=plt.get_cmap("viridis_r"))
    cb=plt.colorbar(C3)
    cb.set_label('$\delta RH / \delta p $ in %/hPa',fontsize=16)
    ax3.set_xticks(ax3.get_xticks()[::])
    ax3.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
    ax3.set_xlim([unit_time[0],unit_time[-1]])
    #ax3.set_xlabel('Local Time')
    ax3.set_ylabel('Pressure in hPa')
    ax3.grid()
    ax3.set_ylim([p_mid_levels[0],p_mid_levels[-1]])
    plt.gca().invert_yaxis()
    plt.setp(plt.gca().xaxis.get_majorticklabels(),'rotation', 30)
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                wspace=None, hspace=0.3)
    fig.savefig(fig_name, dpi=500,bbox_inches='tight')
    fig.savefig(server_path+fig_name,dpi=500,bbox_inches="tight")
    plt.close()
    print("Plotted Gradients and stored them on server")
    return        


###############################################################################
def plot_timeseries(data,filename,server_path, start_time=None, end_time=None, t_range=None,
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
    fig_name="Liveplot"+filename[:-4]+".png"
    print("Liveplotting")
    fig_title="Date "+filename[6:8]+"."+filename[4:6]+"."+filename[0:4]+" ,Start Time: "+filename[8:10]+":"+filename[10:12]+":"+filename[12:14] 
    temp = {}
    hum = {}
    pres = {}
    t = {}
    numarduinos = len(list(data))
    
    halfslave = int(11/2)+1
    jet = plt.get_cmap('gist_rainbow',int(halfslave))
    #print(halfslave)
    
    for i in range(1, numarduinos + 1):
        temp[i] = data[i][1:, 1]
        hum[i] = data[i][1:, 2]
        pres[i] = data[i][1:, 3]
        t[i] = data[i][1:, 0]
    
    plt.rcParams.update({'font.size': 14})    
    fig, ax = plt.subplots(3, 1, figsize=(15, 10))
    for i in range(1, numarduinos + 1):
        cindex = np.mod(i-1,halfslave)
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
    fig.savefig(fig_name, dpi=500,bbox_inches='tight')
    fig.savefig(server_path+fig_name,dpi=500,bbox_inches="tight")
    plt.close()
###############################################################################
def plot_boundary_layer_height(filename,server_path,unit_time,z_BL_RH,z_BL_q,z_BL_theta,z_BL_theta_e):
    fig_name="BL_height"+filename[:-4]+".png"
    fig_title="Date "+filename[6:8]+"."+filename[4:6]+"."+filename[0:4]+" ,Start Time: "+filename[8:10]+":"+filename[10:12]+":"+filename[12:14] 
    print('Plotting Boundary layer height')
    fig= plt.figure(figsize=(20,10))
    ax= fig.add_subplot(212)
    plt.rcParams.update({'font.size': 12})  
    ax.plot(num2date(unit_time), z_BL_RH, label='Relative Humidity')
    ax.set_xlabel('Time')
    ax.set_ylabel('Boundary Layer Height [m]')
    ax.set_xticks(ax.get_xticks()[::])
    ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))

    ax.plot(num2date(unit_time), z_BL_q, label='Specific Humidity')
    ax.plot(num2date(unit_time), z_BL_theta, label='Potential Temperature')
    ax.plot(num2date(unit_time), z_BL_theta_e, label='Pseudopotential Temperature')
    #ax.set_xlim(datetime.datetime(2018, 8, 29, 7, 50), datetime.datetime(2018, 8, 29, 14, 50))
    #ax.set_xlim(datetime.datetime(2018, 9, 3, 13, 40), datetime.datetime(2018, 9, 3, 16, 30))
    #ax[1].set_xlabel('Time')
    #ax[1].set_ylabel('Boundary Layer Height [m]')
    #ax[1].set_xticks(ax[0].get_xticks()[::])
    #ax[1].xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
    ax.legend()
    fig.savefig(fig_name, dpi=500,bbox_inches='tight')
    fig.savefig(server_path+fig_name,dpi=500,bbox_inches="tight")
    plt.close()
    
###############################################################################
def readme(name,instruments):
    """
    creates readme file for every measurement. note that infos like weather 
    still have to be implemented manually
    """
    file = open('readme_'+name+'.txt', 'w')   
    file.write('Filename                            : '+name+'.txt\n')
    file.write('Format                              : date, time, instrument number, temperature, humidity, pressure, packetnumber\n')
    file.write('Date                                : '+name[6:8]+'-'+name[4:6]+'-'+name[0:4]+'\n')
    file.write('Launchtime                          : '+name[8:10]+':'+name[10:12]+':'+name[12:14]+'\n')
    file.write('Units                               : pressure: hPa, humidity: %, temperature: degree Celsius, date: yyyy-mm-dd, time: HH:MM:SS.SSSSSS\n')
    file.write('Weather:                            : \n')
    file.write('Wind                                : \n')
    file.write('Used instruments                    : '+str(instruments)+'\n')
    file.write('Position of instruments on line (m) : // 0 is highest\n')
    file.write('Notes                               : \n')      
    file.close()

def compare_sonde(sondepath,
                  launchname,
                  groundtemp,
                  groundhum,
                  alpaca_filename,    
                  plotpath,
                  month = 8,
                  heliheight = 600):
    """
    Reads in sonde data and alpaca data, autmatically finds the 
    radiosonde launch time and the time when the sonde reached 
    the balloon height. Compares the sonde profile with ALPACA
    profile averaged around the sonde launch time window. Computes
    additional statistics.
    """
    ##### READ RADIOSONDE DATA
    ##### Radiosonde data file and info file
    filename = sondepath+launchname+'_UTC_EDT.tsv'
    infofile = sondepath+launchname+'_UTC_EDT_AuditTrail.tsv'
    
    ##### Read in sonde data
    sondedata = np.genfromtxt(filename,skip_header = 39)
    
    ##### Set missing values to NaN
    sondedata[np.where(sondedata==-32768.)] = np.nan
    
    ## Time:        0
    ## Temperature: 2
    ## Humidity:    3
    ## v:           4
    ## u:           5
    ## Height       6
    ## Pressure     7
    ## Dewpoint     8
    
    ##### Convert pressure to height using temperature
    # FIXME TODO
    
    ##### Convert temperature to celsius
    sondedata[:,2] -= 273.15
    
    ##### Find time when Radiosonde reached highest point, use only values
    ##### before that
    apogee = np.argmax(sondedata[:,6])
    sondedata = sondedata[0:apogee,:]
    
    ##### Find the time when the Radiosonde was above 10 m. This should be 
    ##### the time when the Sonde was launched. Use values after that
    launchtime = np.where(sondedata[:,6] > 10)[0][0]
    heliheighttime = np.where(sondedata[:,6] > heliheight)[0][0]
    timetolaunch = sondedata[launchtime,0]
    timetoheliheight = sondedata[heliheighttime,0]
    sondedata = sondedata[launchtime-1:heliheighttime,:]
    
    ##### Set the first value of the sonde temp and humidity to the ground values
    sondedata[0,2] = groundtemp
    sondedata[0,3] = groundhum
    ##### Get Radiosonde start time from the data
    ##### Get start of record time from infofile
    with open(infofile, 'rb') as f:
        clean_lines = (line.replace(b':',b' ') for line in f)
        sondeinfo = np.genfromtxt(clean_lines, dtype=int, skip_header=4,max_rows=1)
        
    secondofstart = (sondeinfo[5]+ 2) * 3600 + sondeinfo[6] * 60
    ##### Determine how many hours, minutes, seconds until the sonde was launched
    hourstolaunch = int((timetolaunch+ secondofstart)/3600)
    minutestolaunch = int(np.mod((timetolaunch+ secondofstart),3600)/60)
    secondstolaunch = int(np.mod(np.mod((timetolaunch+ secondofstart),3600),60))
    
    ##### Determine time of launch
    sondelaunch = datetime.datetime(sondeinfo[4],month,sondeinfo[2],
                           hourstolaunch,minutestolaunch,
                           secondstolaunch)
    
    ##### Determine how many hours, minutes, seconds until the sonde reached helikite
    hourstoheliheight = int((timetoheliheight+secondofstart)/3600)
    minutestoheliheight = int(np.mod((timetoheliheight+secondofstart),3600)/60)
    secondstoheliheight = int(np.mod(np.mod((timetoheliheight+secondofstart),3600),60))
    
    ##### Determine time when sonde reached helikite
    sondeheli = datetime.datetime(sondeinfo[4],month,sondeinfo[2],
                           hourstoheliheight,minutestoheliheight,
                           secondstoheliheight)
    
    ##### Create a nice string of the launch time for title, filename of plot
    titletime = str(sondelaunch)
    titletime = titletime.replace('-','')
    titletime = titletime.replace(' ','')
    titletime = titletime.replace(':','')
    
    #########################################################################################
    ##### READ ALPACA FILE
    
    data = np.load(alpaca_filename)
    #data = apply_correction(data)
    temp = {}
    hum = {}
    pres = {}
    try:
        for alpaca in data:
            temp[alpaca] = data[alpaca][np.logical_and(data[alpaca][:, 0] >= date2num(sondelaunch), data[alpaca][:, 0] <= date2num(sondeheli)), 1]
            hum[alpaca] = data[alpaca][np.logical_and(data[alpaca][:, 0] >= date2num(sondelaunch), data[alpaca][:, 0] <= date2num(sondeheli)), 2]
            pres[alpaca] = data[alpaca][np.logical_and(data[alpaca][:, 0] >= date2num(sondelaunch), data[alpaca][:, 0] <= date2num(sondeheli)), 3]
            if len(temp[alpaca]) == 0:
                temp[alpaca] = np.array([data[alpaca][data[alpaca][:, 0] >= date2num(sondelaunch), 1][0]])
                hum[alpaca] = np.array([data[alpaca][data[alpaca][:, 0] >= date2num(sondelaunch), 2][0]])
                pres[alpaca] = np.array([data[alpaca][data[alpaca][:, 0] >= date2num(sondelaunch), 3][0]])
            print('Arduino {}: Number of averaged timesteps: {}'.format(alpaca, len(temp[alpaca])))
            temp[alpaca] = np.mean(temp[alpaca])
            hum[alpaca] = np.mean(hum[alpaca])
            pres[alpaca] = np.mean(pres[alpaca])
    except:
        sys.exit({"Something went wrong with the ALPACA data. The time of the \n \
                 ALPACAS and the Sonde launch are not matching. Try choosing \n \
                 a different ALPACA file"})
    alpacapres = np.asarray(list(pres.values()))
    alpacatemp = np.asarray(list(temp.values()))
    alpacahum = np.asarray(list(hum.values()))
    #########################################################################################
    ##### Create figure with the comparison
    
    
    #img = imread("alpaka2.png")
    #img = np.flip(img,0)
    fig,(axtemp,axhum) = plt.subplots(1,2,figsize=(10,8))
    axtemp.plot(sondedata[:,2],sondedata[:,7],linestyle='--',marker='x',color = 'red',markersize=10,zorder=1)
    axtemp.plot(alpacatemp,alpacapres,linestyle='--',marker='x',color = 'blue',markersize=10,zorder=1)
    #axtemp.imshow(img,zorder=0,extent=[13, 20, 940, 1020],aspect=0.15,alpha=0.1)
    axtemp.invert_yaxis()
    axtemp.set_xlabel('Temperature [°C]')
    axtemp.set_ylabel('Pressure [hPa]')
    axtemp.legend(['Radiosonde','ALPACAS'])
    #axtemp.grid(linestyle='--',alpha=0.1)
    axtemp.set_title('Temperature')
    fig.suptitle('Radiosonde-ALPACA comparison, Launchtime: '+titletime)
    
    
    axhum.plot(sondedata[:,3],sondedata[:,7],linestyle='--',marker='x',color = 'red',markersize=10,zorder=1)
    axhum.plot(alpacahum,alpacapres,linestyle='--',marker='x',color = 'blue',markersize=10,zorder=1)
    #axhum.imshow(img,zorder=0,extent=[56, 72, 940, 1020],aspect=0.34,alpha=0.1)
    axhum.invert_yaxis()
    axhum.set_xlabel('Rel. Humidity [%]')
    axhum.legend(['Radiosonde','ALPACAS'])
    axhum.grid(linestyle='--',alpha=0.1)
    axhum.set_title('Relative Humidity')
    
    fig.savefig(plotpath+'Radiosonde_ALPACA_'+titletime+'.png')
    print('Figure saved in '+plotpath+'Radiosonde_APLACA_'+titletime+'.png')
    ###################################################################################
    ##### Compute additional statistics
    
    ##### Interpolate sonde data to pressure of ALPACAS
    sondetemp = interp1d(sondedata[:,7],sondedata[:,2],fill_value='extrapolate',kind='linear')(alpacapres)
    sondehum = interp1d(sondedata[:,7],sondedata[:,3],fill_value='extrapolate',kind='linear')(alpacapres)
    
    ##### Calculate BIAS, RMS
    biastemp = np.mean(alpacatemp-sondetemp)
    rmsetemp = np.sqrt(np.mean((alpacatemp-sondetemp)**2))
    rtemp = np.corrcoef(alpacatemp,sondetemp)[0,1]
    print('Temperature:')
    print('BIAS: ',biastemp)
    print('RMSE: ',rmsetemp)
    print('R: ',rtemp)
    
    biashum = np.mean(alpacahum-sondehum)
    rmsehum = np.sqrt(np.mean((alpacahum-sondehum)**2))
    rhum = np.corrcoef(alpacahum,sondehum)[0,1]
    print('Humidity:')
    print('BIAS: ',biashum)
    print('RMSE: ',rmsehum)
    print('R: ',rhum)
    
    ##### Scatter plot of ALPACA vs. sonde
    fig,(axtemp,axhum) = plt.subplots(1,2,figsize=(10,8))
    axtemp.plot([min(sondetemp)-2, max(sondetemp)+2],[min(sondetemp)-2, max(sondetemp)+2],color='black')
    axtemp.scatter(sondetemp,alpacatemp,linestyle='--',color = 'red')
    axtemp.set_xlabel('Temperature Sonde [°C]')
    axtemp.set_ylabel('Pressure ALPACAS [°C]')
    axtemp.set_xlim([min(sondetemp)-2, max(sondetemp)+2])
    axtemp.set_ylim([min(sondetemp)-2, max(sondetemp)+2])
    axtemp.grid(linestyle='--',alpha=0.1)
    axtemp.set_title('BIAS: '+ str(round(biastemp,2))+'  RMSE: '+str(round(rmsetemp,2))+'  R: '+str(round(rtemp,2)),fontsize=15)
    
    axhum.plot([min(sondehum)-2, max(sondehum)+2],[min(sondehum)-2, max(sondehum)+2],color='black')
    axhum.scatter(sondehum,alpacahum,linestyle='--',color = 'red')
    axhum.set_xlabel('Humidity Sonde [%]')
    axhum.set_ylabel('Humidity ALPACAS [%]')
    axhum.set_xlim([min(sondehum)-2, max(sondehum)+2])
    axhum.set_ylim([min(sondehum)-2, max(sondehum)+2])
    axhum.grid(linestyle='--',alpha=0.1)
    axhum.set_title('BIAS: '+ str(round(biashum,2))+'  RMSE: '+str(round(rmsehum,2))+'  R: '+str(round(rhum,2)),fontsize=15)
    
    fig.suptitle('Radiosonde-ALPACA comparison, Launchtime: '+titletime)
    
    fig.savefig(plotpath+'Radiosonde_APLACA_scatter_'+titletime+'.png')
    print('Figure saved in '+plotpath+'Radiosonde_APLACA_scatter_'+titletime+'.png')
    return sondedata[:,7], sondedata[:,2], sondedata[:,3], sondelaunch, sondeheli

####################################################################################
####################################################################################
    
def get_profile(data, time_start, time_end, verbose = False):
    """
    Plots vertica profiles of temperature and humidty for a given time period.
    
    Parameters:
        data (dictionary): dictionary with data for all alpacas
        time_start (datetime.datetime(yyyy, mm, dd, HH, MM, SS)): start time of
            time period
        time_end (datetime.datetime(yyyy, mm, dd, HH, MM, SS)): end time of 
            time period
    """
    plt.rcParams.update({'font.size': 14})
    
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
        if verbose:
            print('Arduino {}: Number of averaged timesteps: {}'.format(alpaca, len(temp[alpaca])))
        temp[alpaca] = np.mean(temp[alpaca])
        hum[alpaca] = np.mean(hum[alpaca])
        pres[alpaca] = np.mean(pres[alpaca])
        
    pres = np.asarray(list(pres.values()))
    temp = np.asarray(list(temp.values()))
    hum = np.asarray(list(hum.values()))
    
    return pres, temp, hum


def alt_time_plot(filename,server_path,unit_time,z_levels,Temp_zint,RH_zint,Theta,z_BL_q,z_BL_rh,z_BL_theta,z_BL_theta_e,boundary_layer=False):
    ###########################################################################
    ##Plot data
    #if boundary_layer:
    #    z_BL_pseudopot, p_BL_pseudopot = boundary_layer_height(RH_zint, Temp_zint, z_levels, 'pseudopotential_temperature')
    #    z_BL_pot, p_BL_pot = boundary_layer_height(RH_zint, Temp_zint, z_levels, 'potential_temperature')
    #    z_BL_hum, p_BL_hum = boundary_layer_height(RH_zint, Temp_zint, z_levels, 'specific_humidity')
    #    z_BL_relhum, p_BL_relhum = boundary_layer_height(RH_zint, Temp_zint, z_levels, 'relative_humidity')
    fig_name="Height_"+filename[:-4]+".png"
    fig_title="Date "+filename[6:8]+"."+filename[4:6]+"."+filename[0:4]+" ,Start Time: "+filename[8:10]+":"+filename[10:12]+":"+filename[12:14] 
    ###########################################################################
    print("Plotting...")
    fig= plt.figure(figsize=(30,15))
    matplotlib.rcParams.update({'font.size': 14})
    
    levels_T=np.arange(round(np.nanmin(Temp_zint)),round(np.nanmax(Temp_zint)),(round(np.nanmax(Temp_zint))-round(np.nanmin(Temp_zint)))/20)
    levels_Theta=np.arange(round(np.nanmin(Theta),2),round(np.nanmax(Theta),2),round((np.nanmax(Theta)-np.nanmin(Theta))/20,2)) -273.15
    ###########################################################################
    #Subplot1: Temperatur
    ax1=fig.add_subplot(311)
    X,Y = np.meshgrid(unit_time,z_levels)
    C= ax1.contourf(X,Y,Temp_zint,levels_T,cmap=plt.get_cmap("hot_r", len(levels_T)-1),extend="both")
    cb=plt.colorbar(C)
    cb.set_label('Temperatur in $^\circ$C',fontsize=16)
    #
    ax1.set_xticks(ax1.get_xticks()[::])
    ax1.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
    ax1.set_xlim([unit_time[0],unit_time[-1]])
    #ax1.set_xlabel('Local Time')
    ax1.set_ylabel('Altitude in m')
    ax1.grid()
    if boundary_layer:
        ax1.plot(unit_time, z_BL_rh, color='C0', label='Relative Humidity')
        ax1.plot(unit_time, z_BL_q, color='C1', label='Specific Humidity')
        ax1.plot(unit_time, z_BL_theta, color='C2', label='Potential Temperature')
        ax1.plot(unit_time, z_BL_theta_e, color='C3', label='Pseudopotential Temperature')
        ax1.legend()
    #Plot Title
    fig_title="Date "+filename[6:8]+"."+filename[4:6]+"."+filename[0:4]+" ,Start Time: "+filename[8:10]+":"+filename[10:12]+":"+filename[12:14] 
    plt.title(fig_title, fontsize=16)
    #extra settings for axes and ticks
    plt.setp(plt.gca().xaxis.get_majorticklabels(),'rotation', 30)
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                wspace=None, hspace=0.3)# for space between the subplots  
    ###################################### 
    #Subplot2 pot. Temperatur
    ax2=fig.add_subplot(312)
    X,Y = np.meshgrid(unit_time,z_levels)
    C2= ax2.contourf(X,Y,Theta-273.15,levels_Theta,cmap=plt.get_cmap("hot_r",len(levels_Theta)-1),extend="both")
    cb=plt.colorbar(C2)
    cb.set_label('$\Theta$ in $^\circ$C',fontsize=16)
    
    ax2.set_xticks(ax2.get_xticks()[::])
    ax2.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
    ax2.set_xlim([unit_time[0],unit_time[-1]])
    ax2.grid()
    if boundary_layer:
        ax2.plot(unit_time, z_BL_rh, color='C0', label='Relative Humidity')
        ax2.plot(unit_time, z_BL_q, color='C1', label='Specific Humidity')
        ax2.plot(unit_time, z_BL_theta, color='C2', label='Potential Temperature')
        ax2.plot(unit_time, z_BL_theta_e, color='C3', label='Pseudopotential Temperature')
    #ax2.set_xlabel('Local Time')
    ax2.set_ylabel('Altitude in m')
    plt.setp(plt.gca().xaxis.get_majorticklabels(),'rotation', 30)
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                wspace=None, hspace=0.3)   
    ######################################
    #Subplot3 Relative Humidity
    ax3=fig.add_subplot(313)
    C3= ax3.contourf(X,Y,RH_zint,cmap=plt.get_cmap("viridis_r"))
    cb=plt.colorbar(C3)
    cb.set_label('RH in %',fontsize=16)
    ax3.set_xticks(ax3.get_xticks()[::])
    ax3.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
    ax3.set_xlim([unit_time[0],unit_time[-1]])
    #ax3.set_xlabel('Local Time')
    ax3.set_ylabel('Altitude in m')
    ax3.grid()   
    if boundary_layer:
        ax3.plot(unit_time, z_BL_rh, color='C0', label='Relative Humidity')
        ax3.plot(unit_time, z_BL_q, color='C1', label='Specific Humidity')
        ax3.plot(unit_time, z_BL_theta, color='C2', label='Potential Temperature')
        ax3.plot(unit_time, z_BL_theta_e, color='C3', label='Pseudopotential Temperature')
    plt.setp(plt.gca().xaxis.get_majorticklabels(),'rotation', 30)
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                wspace=None, hspace=0.3)
    fig.savefig(fig_name, dpi=500,bbox_inches='tight')
    fig.savefig(server_path+fig_name,dpi=500,bbox_inches="tight")
    plt.close()
    print("z-coordinate plotted and stored on server")
    return        

###############################################################################