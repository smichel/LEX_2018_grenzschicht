#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 21 21:31:45 2018

@author: Simon Michel, Henning Dorff, Laura Dietrich, Jakob Doerr, Theresa Lang, Joscha Fregin
"""
import serial
import time 
usb_port = '/dev/cu.wchusbserialfa130'
baud_rate = 9600
t = 0
i = 0
# TODO filename could be date or something.
f = open('data.txt','w')
    
while(True):
    if (t == 0):
        # Parity needs to be PARITY_NONE
        ser = serial.Serial(usb_port,baud_rate,timeout=0,parity=serial.PARITY_NONE, rtscts=1)
    
    time.sleep(1)    
    s = ser.read(100)
    if (len(s) == 16):
        i += 1
        T = float(s[0:4])/100
        h = float(s[4:8])/100
        P = round(float(s[8:])/10000,2)
        s = str(T) + ' '+ str(h)+ ' '+ str(P)
        print(s)
        f.write(s+"\n") #maybe on other systems "" needs to be ''
    t = t+1
    if (i == 3):
        break
    
f.close()

    