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

i = 0
t = 0
baud_rate = 9600
usb_port = '/dev/cu.wchusbserial1410'
nslave = 4
data = {}
Flag = True
for i in range(nslave):
    data[i] = np.zeros(4)
    
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

        data[name-1] = np.vstack((data[name-1],np.array([T,h,P,count])))
    t = t+1