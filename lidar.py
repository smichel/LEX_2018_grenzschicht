#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 13:21:45 2018

@author: jf
"""

import os
import numpy as np
import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import date2num,num2date
from matplotlib import dates
import matplotlib
#import plot_functions as pf
from matplotlib.colors import ListedColormap
from matplotlib.cm import get_cmap


os.chdir('C:/Users/Dietrich/Documents/Studium/LEX_2018_grenzschicht')
#range 9m + i*18m
file='C:/Users/Dietrich/Documents/Studium/LEX_2018_grenzschicht/0831.LID'
    
def read_lidar(path_to_file):
    """
    returns list with arrays containing time [t], height[t,h] level[t,h], windspeed[t,h], winddirection[t,h]
    The file contains 31 variables + 1x metadata in 32 lines/timestep
    Output time is convertet from UTC to CEST (+2 hours)
    Height is calculated by the function (forumula below)
    Variables (note that every variable has len=3):
        'H  ': height = H*18 m-9 m
        'D  ': winddirection [degrees]
        'V  ': windspeed [m/s]
        'VVV': y wind [m/s]
        'VVU': x wind [m/s]
        'VVW': w wind [m/s]]
        'R  ': backscatter [?]  
    """
    # open file
    data = open(path_to_file,'r').readlines()
    
    # first line is metadata - extract metadata for every timestep
    meta_data = data[::32]
    lidar_data={}
    length=len(data[::32])
    
    # initiate windvectors
    windspeed = np.zeros([length, 90])
    winddirection = np.zeros([length, 90])
    height = np.zeros([length, 90])
    vertical_windspeed = np.zeros([length,90])
    
    # prepare data for extraction
    #the three first characters of every line contain the variable name and thus need to 
    #be stored as dict variables and removed for further processing
    for i in range(1,32):
        lidar_data[data[i][0:3]]=data[i::32][:]
        for j in range(0,len(lidar_data[data[i][0:3]])):
            lidar_data[data[i][0:3]][j]=lidar_data[data[i][0:3]][j][3:]
    
    #extract windinformation. every value has len=6
    for i in range(0,len(lidar_data['H  '])):
        for j in range(0,90):
            try:
                windspeed[i,j] = float(str(lidar_data['V  '][i])[j*6:j*6+6])
            except:
                windspeed[i,j] = np.nan
            try:
                winddirection[i,j] = float(str(lidar_data['D  '][i])[j*6:j*6+6])
            except:
                 winddirection[i,j] = np.nan
            try:
                height[i,j] = float(str(lidar_data['H  '][i])[j*6:j*6+6])
            except:
                 height[i,j] = np.nan
            try:
                vertical_windspeed[i,j] = float(str(lidar_data['VVW'][i])[j*6:j*6+6])
            except:
                 vertical_windspeed[i,j] = np.nan
        
    # calculate hight
    height = height * 18 -9
    
    #time extraction + correction. time is converted from datetime_obj to float 
    #with matplotlib.dates.date2num
    time=np.zeros(len(meta_data))
    for i in range(0,len(meta_data)):
        time[i] = np.int(meta_data[i][4:16])
        time[i] = date2num(datetime.datetime(int('20'+str(time[i])[0:2]),int(str(time[i])[2:4]),
            int(str(time[i])[4:6]),int(str(time[i])[6:8]),int(str(time[i])[8:10]),
            int(str(time[i])[10:12])) + datetime.timedelta(hours=2))
        
    data = [time,height,winddirection,windspeed,vertical_windspeed]
    
    return data,lidar_data, meta_data

data ,lidar_data,meta= read_lidar(file)

#%%
def profile_plot_lidar(data,starttime=0,endtime=0,v_levels=20,d_levels=37,vmax=15,hmax=700,wmax=2):
    print('prepare data...')
    time = data[0]
    time = num2date(time)
    height = data[1][0]
    max_height_index = np.where(height>hmax)[0][0]+1
    height= height[:max_height_index]
    windspeed = np.transpose(data[3])[:max_height_index,:]
    windspeed = np.nan_to_num(windspeed,1000.0)
    windspeed[windspeed>100] = np.nan
    winddirection = np.transpose(data[2])[:max_height_index,:]
    winddirection = np.nan_to_num(winddirection,1000.0)
    winddirection[winddirection > 370] = np.nan
    vertical_w = np.transpose(data[4])[:max_height_index,:]
    inferno = get_cmap('viridis').colors
    other = get_cmap('plasma').colors
    new_cmap = ListedColormap(inferno+other[::-1])
    if (starttime==0 and endtime==0):
        st_index=0
        end_index=-1
    else:
        st_index = np.where(date2num(time) >= date2num(starttime))[0][0]
        end_index = np.where(date2num(time) <= date2num(endtime))[0][-1]
    X,Y = np.meshgrid(time[st_index:end_index],height) #TODO
    hspace=0.1
    aspect=8
    
    print("plotting...")
    matplotlib.rcParams.update({'font.size': 12})
    fig = plt.figure(figsize=(24,12))
    ax1 = fig.add_subplot(311)
    ax1.set_title('Lidar winddata: '+str(time[0].day)+'.'+str(time[0].month)+'.'+str(time[0].year))
    levels=np.linspace(0,vmax,v_levels)
    c1 = ax1.contourf(X,Y,windspeed[:,st_index:end_index],levels,extend='max')  
    ax1.set_ylabel('height [m]')
    ax1.set_xticks([])
    #ax1.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
    cb=plt.colorbar(c1,aspect=aspect)
    cb.set_label('Windspeed [$ms^{-1}$]',fontsize=12)
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
            wspace=None, hspace=hspace)# for space between the subplots 
    plt.setp(plt.gca().xaxis.get_majorticklabels(),'rotation', -30)
    
    ax2 = fig.add_subplot(312)
    #ax2.set_title(str(time[0].day)+'.'+str(time[0].month)+'.'+str(time[0].year))
    levels= np.linspace(0,360,d_levels)
    c1 = ax2.contourf(X,Y,winddirection[:,st_index:end_index],levels,cmap=new_cmap)  
    ax2.set_ylabel('height [m]')
    ax2.set_xticks([])
    #ax2.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
    cb=plt.colorbar(c1,aspect=aspect)
    cb.set_label('Winddirection [$^\circ$]',fontsize=12)
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
            wspace=None, hspace=hspace)# for space between the subplots 
    plt.setp(plt.gca().xaxis.get_majorticklabels(),'rotation', -30)


    ax3 = fig.add_subplot(313)
    #ax3.set_title(str(time[0].day)+'.'+str(time[0].month)+'.'+str(time[0].year))
    levels=np.linspace(-wmax,wmax,v_levels)
    c1 = ax3.contourf(X,Y,vertical_w[:,st_index:end_index],levels,extend='both')  
    ax3.set_ylabel('height [m]')
    ax3.set_xticks(ax3.get_xticks()[::])
    ax3.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
    cb=plt.colorbar(c1,aspect=aspect)
    cb.set_label('vertical windspeed [$ms^{-1}$]',fontsize=12)
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
            wspace=None, hspace=hspace)# for space between the subplots 
    plt.setp(plt.gca().xaxis.get_majorticklabels(),'rotation', -30)

    fig.savefig('lidar_test', dpi=500,bbox_inches='tight')
        

profile_plot_lidar(data,starttime=datetime.datetime(2018,8,31,7,1,2),endtime=datetime.datetime(2018,8,31,8,1,2))


#data=np.asarray(data)


