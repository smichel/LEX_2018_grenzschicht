#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 21 21:31:45 2018

@author: Simon Michel, Henning Dorff, Laura Dietrich, Jakob Doerr, Theresa Lang, Joscha Fregin
"""
import serial
import time 
import matplotlib.pyplot as plt
import numpy as np
usb_port = '/dev/cu.wchusbserialfa130'
baud_rate = 9600
t = 0
i = 0
pressure = []
# TODO filename could be date or something.
f = open('data.txt','w')
plt.figure()

while(True):
    if (t == 0):
        # Parity needs to be PARITY_NONE
        ser = serial.Serial(usb_port,baud_rate,timeout=0,parity=serial.PARITY_NONE, rtscts=1)
    
    time.sleep(0.5)    
    s = ser.read(100)
    if ((len(s) < 24) and (len(s) > 15)):
        i += 1
        T = float(s[0:4])/100
        h = float(s[4:8])/100
        P = round(float(s[8:16])/10000,2)
        count = int(s[16:])
        s = str(T) + ' '+ str(h)+ ' '+ str(P) + ' ' + str(count)
        print(s)
        f.write(s+"\n") #maybe on other systems "" needs to be ''

        #papa, = plt.plot(pressure)
    pressure.append(h)  
    #plt.clf()
    if (t>1):
        plt.plot(t,pressure[t-1:t],'x')
        plt.show()
    
    plt.pause(0.01)
    t = t+1
    #if (i == 100000):
    #    break
    
f.close()

    