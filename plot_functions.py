# -*- coding: utf-8 -*-
"""
Collection of functions to plot ALPACA data. 
"""
import time 
import datetime
import matplotlib.pyplot as plt
import numpy as np
from os.path import join
from matplotlib.dates import date2num, num2date

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

