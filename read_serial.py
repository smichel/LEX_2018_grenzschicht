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
from matplotlib.widgets import Slider


fig = plt.figure(figsize=(10,6))
ax = fig.add_subplot(311)
ax1= fig.add_subplot(312)
ax2= fig.add_subplot(313)

ax.grid(alpha=0.4,linestyle='--')
ax1.grid(alpha=0.4,linestyle='--')
ax2.grid(alpha=0.4,linestyle='--')

# Make some space for sliders
fig.subplots_adjust(bottom=0.2, left=0.1)

# Initialise plots
line, = ax.plot([0,1], [23,32], lw=2)
line1,=ax.plot([0,1], [23,32], lw=2)
line4, = ax1.plot([0,1], [1012,1013], lw=2)
line5,=ax1.plot([0,1], [1013,1013], lw=2)
line2, = ax2.plot([0,1], [20,100], lw=2)
line3,=ax2.plot([0,1], [20,100], lw=2)
forward_space = 0.5
backward_space = 0.1
diff_to_lead = 2
slider_limits = 100

# Insert slider
slider_ax = plt.axes([0.1, 0.1, 0.8, 0.02])
# Define sliders properties 
slider = Slider(slider_ax, "x_lim", -slider_limits, +slider_limits, valinit=0, color='#AAAAAA')


ax.set_title('Temperature')
ax2.set_title('Humidity')
ax1.set_title('Pressure')

usb_port = '/dev/cu.wchusbserial1410'
baud_rate = 9600
t = 0
i = 0
temperature1 = [500]
temperature2 = [500]
pres1 = [1000]
pres2 = [1000]
humid1 = [20]
humid2 = [20]

x = [0]
# TODO filename could be date or something.
f = open('data.txt','w')
#plt.figure()

while(True):
    
    if (t == 0):
        # Parity needs to be PARITY_NONE
        ser = serial.Serial(usb_port,baud_rate,timeout=0,parity=serial.PARITY_NONE, rtscts=1)
    
        time.sleep(1)    
    s = ser.read(100)
    if ((len(s) < 24) and (len(s) > 15)):
        i += 1
        T = float(s[0:4])/100
        h = float(s[4:8])/100
        P = round(float(s[8:16])/10000,2)
        name = round(float(s[16:17]))
        count = int(s[17:])
        s = 'Arduino ' + str(name) + ': ' + str(T) + ' '+ str(h)+ ' '+ str(P) + ' ' + str(count)
        print(s)
        f.write(s+"\n") #maybe on other systems "" needs to be ''
        print(name)
        if name == 1:
            temperature1.append(T)
            temperature2.append(temperature2[-1])
            humid1.append(h)
            humid2.append(humid2[-1])
            pres1.append(P)
            pres2.append(pres2[-1])
        else:
            temperature2.append(T)
            temperature1.append(temperature1[-1])
            humid2.append(h)
            humid1.append(humid1[-1])
            pres2.append(P)
            pres1.append(pres1[-1])
        t = t+1
        x.append(t)
    if t > 1:
        line.set_data(x,temperature1)
        line1.set_data(x,temperature2)
        line2.set_data(x,humid1)
        line3.set_data(x,humid2)
        line4.set_data(x,pres1)
        line5.set_data(x,pres2)
        
        if (max(x)-min(x) < diff_to_lead):
            ax.set_xlim(min(x)-backward_space,diff_to_lead+forward_space)
            ax1.set_xlim(min(x)-backward_space,diff_to_lead+forward_space)
            ax2.set_xlim(min(x)-backward_space,diff_to_lead+forward_space)
        elif(np.mod(i,1)==0):
            def on_change(val):
                ax.set_xlim(min(x), max(x)+forward_space)
                ax1.set_xlim(min(x), max(x)+forward_space)
                ax2.set_xlim(min(x), max(x)+forward_space)

            slider.on_changed(on_change)
            ax.set_xlim(min(x), max(x)+forward_space)
            ax1.set_xlim(min(x), max(x)+forward_space)
            ax2.set_xlim(min(x), max(x)+forward_space)
        else:
            pass
        fig.canvas.draw()
        plt.pause(0.01)
        
    #if (i == 100000):
    #    break
    
f.close()

    