#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 13:21:45 2018

@author: jf
"""

import os
import numpy as np
import datetime
from matplotlib.dates import date2num

os.chdir('/Users/jf/Desktop/LEX/LEX_2018_grenzschicht')
#range 9m + i*18m

    
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
        
    # calculate hight
    height = height * 18 -9
    
    #time extraction + correction. time is converted from datetime_obj to float 
    #with matplotlib.dates.date2num
    time=np.zeros(len(meta_data))
    for i in range(0,len(meta_data)):
        time[i] = np.int(meta_data[i][4:16])
        time[i] = date2num(datetime.datetime(int(str(time[i])[0:2]),int(str(time[i])[2:4]),
            int(str(time[i])[4:6]),int(str(time[i])[6:8]),int(str(time[i])[8:10]),
            int(str(time[i])[10:12])) + datetime.timedelta(hours=2))
        
    data = [time,height,winddirection,windspeed]
    
    return data
        


#data=np.asarray(data)


