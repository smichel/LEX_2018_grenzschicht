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
nslave = 4


data = {}
save_array = {}
f = open(file_name,'w')
fehlwert = -9999
for i in range(nslave):
    data[i+1] = np.zeros(4) + fehlwert
    save_array[i+1] = np.zeros(5)    + fehlwert 

# Initialize figures and axes and lines
plt.figure()

tempmin=20
tempmax = 25

while(True):
    
    if (t == 0):
        # Parity needs to be PARITY_NONE
        ser = serial.Serial(usb_port,baud_rate,timeout=0,parity=serial.PARITY_NONE, rtscts=1)
    
        time.sleep(1)    
    s = ser.read(100)
    #print(s)
    if ((len(s) < 26) and (len(s) > 15)):
        i += 1
        T = float(s[0:4])/100
        h = float(s[4:8])/100
        P = round(float(s[8:16])/10000,2)
        name = round(float(s[16:18])) - 10 
        count = int(s[19:])
        s = 'Arduino ' + str(name) + ': ' + str(T) + ' '+ str(h)+ ' '+ str(P) + ' ' + str(count)
        print(s)

        data[name] = np.vstack((data[name],np.array([T,h,P,count])))
        f.write(str(datetime.now())+';'+str(name)+';'+str(T)+';'+str(h)+';'+str(P)+';'+str(count)+'\n') #maybe on other systems "" needs to be ''
        save_array[name] = np.vstack((save_array[name],np.array([time.time(),T,h,P,count])))
        if np.mod(i,10) == 0 and i > 0:
            print('SAVING...')
            f.close()
            f = open(file_name,'a')
            with open('data.npy','wb') as myFile:
                pickle.dump(save_array,myFile)
                myFile.close()
                
            for j in range(nslave):
                plt.plot(save_array[j+1][1::,0],save_array[j+1][1::,1])
            
                if min(save_array[j+1][1::,1]) < tempmin +1:
                    tempmin = min(save_array[j+1][1::,1]) - 1
                if max(save_array[j+1][1::,1]) > tempmax -1:
                    tempmax = max(save_array[j+1][1::,1]) + 1
                plt.ylim(tempmin,tempmax)
            plt.gca().set_prop_cycle(None)
            plt.legend((np.arange(nslave)+1).astype(str))

            plt.pause(0.001)

        

            
    t = t+1