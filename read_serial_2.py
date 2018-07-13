#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 16:47:20 2018

@author: Jakob
"""

import serial
import time 
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider
from datetime import datetime
import pickle
import time

i = 0
t = 0
file_name = './live_data.txt'
baud_rate = 9600
usb_port = '/dev/cu.wchusbserial1410'
nslave = 5


data = {}
save_array = {}
f = open(file_name,'w')
fehlwert = -9999
for i in range(nslave):
    data[i+1] = np.zeros(4) + fehlwert
    save_array[i+1] = np.zeros(5)    + fehlwert 

# Initialize figures and axes and lines
plt.figure(figsize=(15,13))
axtemp = plt.subplot(311)
axhum = plt.subplot(312)
axpres = plt.subplot(313)

axtemp.set_ylabel('Temperature (Celsius)')
axtemp.set_title('Temperature')

axhum.set_ylabel('Humidity (%)')
axhum.set_title('Humidity')

axpres.set_xlabel('Time (UNIX seconds since 01-01-1970)')
axpres.set_ylabel('Pressure (hPa)')
axpres.set_title('Pressure')

##
tempmin=25
tempmax = 27
hummin = 40
hummax = 50
presmin = 1008
presmax = 1012

while(True):
    
    if (t == 0):
        # Parity needs to be PARITY_NONE
        ser = serial.Serial(usb_port,baud_rate,timeout=0,parity=serial.PARITY_NONE, rtscts=1)
    
        time.sleep(1)  
        
    s = ser.read(100)

    #print(s)
    if ((len(s) < 28) and (len(s) > 15)):
        i += 1
        try:
            T = float(s[0:5])/100 - 273.15
            h = float(s[5:10])/100 - 100
            P = round(float(s[10:18])/10000,2) - 1000
            name = round(float(s[18:20])) - 10 
            count = int(s[21:])
            s = 'Arduino ' + str(name) + ': ' + str(T) + ' '+ str(h)+ ' '+ str(P) + ' ' + str(count)
            print(s)
    
            data[name] = np.vstack((data[name],np.array([T,h,P,count])))
            f.write(str(datetime.now())+';'+str(name)+';'+str(T)+';'+str(h)+';'+str(P)+';'+str(count)+'\n') #maybe on other systems "" needs to be ''
            save_array[name] = np.vstack((save_array[name],np.array([time.time(),T,h,P,count])))
        except ValueError:
            print('NOPE...')
        if np.mod(i,100) == 0 and i > 0:
            print('SAVING...')
            f.close()
            f = open(file_name,'a')
            with open('data.npy','wb') as myFile:
                pickle.dump(save_array,myFile)
                myFile.close()
            # PLOT
            for j in range(nslave):
                # Temperature
                axtemp.plot(save_array[j+1][1::,0],save_array[j+1][1::,1],linewidth=2)
                if min(save_array[j+1][1::,1]) < tempmin +1:
                    tempmin = min(save_array[j+1][1::,1]) - 1
                if max(save_array[j+1][1::,1]) > tempmax -1:
                    tempmax = max(save_array[j+1][1::,1]) + 1
                axtemp.set_ylim(tempmin,tempmax)
                
                # Humidity
                axhum.plot(save_array[j+1][1::,0],save_array[j+1][1::,2],linewidth=2)
                if min(save_array[j+1][1::,2]) < hummin +1:
                    hummin = min(save_array[j+1][1::,2]) - 1
                if max(save_array[j+1][1::,2]) > hummax -1:
                    hummax = max(save_array[j+1][1::,2]) + 1
                axhum.set_ylim(hummin,hummax)
                
                 # Pressure
                axpres.plot(save_array[j+1][1::,0],save_array[j+1][1::,3],linewidth=2)
                if min(save_array[j+1][1::,3]) < presmin +1:
                    presmin = min(save_array[j+1][1::,3]) - 1
                if max(save_array[j+1][1::,2]) > hummax -1:
                    presmax = max(save_array[j+1][1::,3]) + 1
                axpres.set_ylim(presmin,presmax)
                
            axtemp.set_prop_cycle(None)
            axtemp.grid(linestyle=':')
            axhum.set_prop_cycle(None)
            axhum.grid(linestyle=':')
            axpres.set_prop_cycle(None)
            axpres.grid(linestyle=':')
            
            
            axhum.legend((np.arange(nslave)+1).astype(str),loc='center left', bbox_to_anchor=(1, 0.5))
            plt.pause(0.001)

        

            
    t = t+1