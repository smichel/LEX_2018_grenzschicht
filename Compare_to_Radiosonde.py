#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 09:46:16 2018

@author: Jakob
"""

import serial
import time 
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import date2num
from matplotlib import dates
from datetime import datetime
import pickle
from scipy.interpolate import interp1d
from processing_functions import *
#import plot_functions as ALPACA
from scipy.misc import imread

month = 8
heliheight = 600
groundtemp = 17.1
groundhum = 77
path = './Messdaten/Radiosonden/'
launchname = '20180831_1036'
plt.xkcd()

##### READ RADIOSONDE DATA
##### Radiosonde data file and info file
filename = path+launchname+'_UTC_EDT.tsv'
infofile = path+launchname+'_UTC_EDT_AuditTrail.tsv'

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

sondestart = datetime(sondeinfo[4],month,sondeinfo[2],sondeinfo[5]+2,sondeinfo[6],0)

secondofstart = (sondeinfo[5]+ 2) * 3600 + sondeinfo[6] * 60
##### Determine how many hours, minutes, seconds until the sonde was launched
hourstolaunch = int((timetolaunch+ secondofstart)/3600)
minutestolaunch = int(np.mod((timetolaunch+ secondofstart),3600)/60)
secondstolaunch = int(np.mod(np.mod((timetolaunch+ secondofstart),3600),60))

##### Determine time of launch
sondelaunch = datetime(sondeinfo[4],month,sondeinfo[2],
                       hourstolaunch,minutestolaunch,
                       secondstolaunch)

##### Determine how many hours, minutes, seconds until the sonde reached helikite
hourstoheliheight = int((timetoheliheight+secondofstart)/3600)
minutestoheliheight = int(np.mod((timetoheliheight+secondofstart),3600)/60)
secondstoheliheight = int(np.mod(np.mod((timetoheliheight+secondofstart),3600),60))

##### Determine time when sonde reached helikite
sondeheli = datetime(sondeinfo[4],month,sondeinfo[2],
                       hourstoheliheight,minutestoheliheight,
                       secondstoheliheight)

##### Create a nice string of the launch time for title, filename of plot
titletime = str(sondelaunch)
titletime = titletime.replace('-','')
titletime = titletime.replace(' ','')
titletime = titletime.replace(':','')

#########################################################################################
##### READ ALPACA FILE
##### Alpaca filename
alpaca_filename = './Messdaten/20180831105131_Grenzschichtentwicklung2.npy'

data = np.load(alpaca_filename)
#data = apply_correction(data)
temp = {}
hum = {}
pres = {}
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

fig.savefig('./Radiosonde_ALPACA_'+titletime+'.png')

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

fig.savefig('./Radiosonde_APLACA_scatter_'+titletime+'.png')