#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 11:31:54 2018

@author: Jakob
"""

import serial
import time
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import date2num
from matplotlib import dates
from datetime import datetime
from scipy.interpolate import interp1d
from scipy.stats import linregress
plt.close('all')


peterdatei = 'P755_20180811_1.dbf'
peterstart = dates.date2num(datetime.strptime('20180811103234', '%Y%m%d%H%M%S')) 
peterend = dates.date2num(datetime.strptime('20180811120648', '%Y%m%d%H%M%S')) 
willydatei = '20180811103236.npy'
startindex = 4500
stopindex = -1

data = np.load(willydatei)
willies = np.array([1,2,3,4,5,6,7,8,9,10,11])
nslave = len(willies)
halfslave = int(nslave/2)+1
jet = plt.get_cmap('gist_rainbow',int(halfslave))
peter = np.genfromtxt(peterdatei,encoding='latin-1')
peter = peter[~np.isnan(peter)]
peter=peter[0:-1]
if np.mod(len(peter),2) == 1:
    peter=np.reshape(peter[0:-np.mod(len(peter),2)],(int(len((peter))/2),2))
else:
    peter=np.reshape(peter,(int(len((peter))/2),2))
petertemp = peter[startindex:stopindex,0]
petertime=np.linspace(peterstart,peterend,len(peter))
petertime = petertime[startindex:stopindex]
arduino={}
temps={}
tempsint = {}
slope = {}
intercept={}
meandev = {}
for i in willies:
    arduino[i]=np.asarray(data[i])
    arduino[i][(arduino[i][:, 1] < 0) | (arduino[i][:, 1] > 35), 1]=np.nan
    temps[i]=arduino[i][:,1]
    tempsint[i] = interp1d(arduino[i][1::,0],arduino[i][1::,1],axis=0,fill_value='extrapolate')(petertime)
    slope[i], intercept[i], r_value, p_value, std_err = linregress( tempsint[i],petertemp)
    meandev[i] = np.mean(tempsint[i]-petertemp)
#for i in willies:
#    for j in range(1,len(arduino[i])):
#        if arduino[i][j,4]<arduino[i][j-1,4]:
#            arduino[i][j,4]=arduino[i][j-1,4]+1

plt.subplots(1,1,figsize=(10,10))

for i in willies:
    cindex = np.mod(i,halfslave)
    if i > halfslave:
        stylus = '--'
    else:
        stylus = '-'
    #plt.plot(arduino[i][:,0],temps[i],color=jet(cindex),linestyle=stylus,linewidth=1.5)
    plt.plot(petertime,tempsint[i],color=jet(cindex),linestyle=stylus,linewidth=1.5)
plt.plot(petertime,petertemp,linewidth=3,color='black')
plt.show(block=False)
plt.grid()
plt.legend(willies.astype(str))

plt.subplots(1,1,figsize=(10,10))

for i in willies:
    cindex = np.mod(i,halfslave)
    if i > halfslave:
        stylus = 'x'
    else:
        stylus = 'o'
    plt.scatter(petertemp,tempsint[i],color=jet(cindex),marker=stylus)
plt.xlim([min(petertemp)-1,max(petertemp)+1])
plt.ylim([min(petertemp)-1,max(petertemp)+1])
plt.grid()
plt.legend(willies.astype(str))
plt.plot([min(petertemp)-3,max(petertemp)+3],[min(petertemp)-3,max(petertemp)+3],color='black')

print('T_peter = A * T_willy + b')
print('A')
print(slope)
print('b')
print(intercept)
print('Mean deviation')
print(meandev)
