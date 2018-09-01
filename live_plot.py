#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 16:47:20 2018

@author: Jakob
"""

import serial
import plot_functions as pf
import time 
import numpy as np
from matplotlib.dates import date2num
from datetime import datetime
import pickle
#22,73

data_filename = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')
data_filename = data_filename + '_Grenzschichtentwicklung3'
baud_rate = 115200
usb_port = '/dev/cu.wchusbserial1420'
slaves = np.array([1,2,3,4,5,6,7,8,9,10,11]) -1
pf.readme(data_filename, slaves+1)
first = slaves[0] + 1
plothistory = 10000  # How much of the data should be plotted (in seconds)
fehlwert = -9999

data = {}
save_array = {}
f = open(data_filename+'.txt','w')

nslave = len(slaves)
halfslave = int(11/2)+1

gott = np.zeros(4)+fehlwert

for i in slaves:
    data[i+1] = np.zeros(4) + fehlwert
    save_array[i+1] = np.zeros(5)    + fehlwert 

### Kalibration
Pcalib = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
# Calibration auf Lüftung:
Tcalib = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

i = 0
t = 0
any_gott = False
while(True):
    if (t == 0):
        # Parity needs to be PARITY_NONE
        ser = serial.Serial(usb_port,baud_rate,timeout=0,parity=serial.PARITY_NONE, rtscts=1)
    
        time.sleep(1)  

    s = ser.read(100)

    if ((len(s) < 48) and (len(s) > 15) and len(s) != 32):
        i += 1
        try:
            if int(s[0:1]) == 0 or int(s[0:1]) == 1:
                lat = float(s[1:8])/100000
                lon = float(s[8:15])/100000
                ele = round(float(s[15:21])/100 - 1000,2)
                name = round(float(s[21:23]))-10
                count = int(s[23:])
                gott = np.vstack((gott,np.array([date2num(datetime.now()),lat,lon,ele])))
                print('GOTT: ' + str(lat) + ' °N, ' + str(lon) + ' °E, Elevation: ' + str(ele) + ' m')
                any_gott = True

            else:
                name = round(float(s[18:20])) - 10
                count = int(s[20:])
                T = round(float(s[0:5])/100 - 273.15,2) #+ Tcalib[int(name)-1]
                h = round(float(s[5:10])/100 - 100,2)
                P = float(s[10:18])/10000 - 1000
    
                P = round(P + Pcalib[int(name)-1],2)
                T = T + Tcalib[int(name)-1]
                #h = h + Hcalib[int(name)-1]
                if (T > 40) | (T < 0) | (h > 100) | (h < 0) | (P >1100) |(P < 700):
                    T = np.nan
                    h = np.nan
                    P = np.nan
    
                s = 'Arduino ' + str(name) + ': ' + str(T) + '°C,  '+ str(h)+ ' %, '+ str(P) + ' hPa, ' + str(count)
                print(s)
    
                data[name] = np.vstack((data[name],np.array([T,h,P,count])))
                f.write(str(datetime.now())+';'+str(name)+';'+str(T)+';'+str(h)+';'+str(P)+';'+str(count)+'\n') #maybe on other systems "" needs to be ''
                save_array[name] = np.vstack((save_array[name],np.array([date2num(datetime.now()),T,h,P,count])))
        except:
            print('NOPE...')
        if np.mod(i,40) == 0 and i > 30:
            time1 = time.time()
            print('SAVING...')
            f.close()
            f = open(data_filename+'.txt','a')
            with open(data_filename+'.npy','wb') as myFile:
                pickle.dump(save_array,myFile)
                myFile.close()
            if any_gott:
                with open(data_filename+'_gps.npy','wb') as myFile:
                    pickle.dump(gott,myFile)
                    myFile.close()
                    
    t = t+1