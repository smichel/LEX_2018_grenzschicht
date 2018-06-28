#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 22 15:40:42 2018

@author: jf
"""

import numpy as np
import matplotlib.pyplot as plt
#from matplotlib.widgets import CheckButtons
from matplotlib.widgets import Slider


# Create figure
fig = plt.figure(figsize=(10,6))
ax = fig.add_subplot(211)
ax1= fig.add_subplot(212)
ax.grid(alpha=0.4,linestyle='--')
ax1.grid(alpha=0.4,linestyle='--')
# Make some space for sliders
fig.subplots_adjust(bottom=0.2, left=0.1)

# Initialise plots
t = np.linspace(0, 10, 1000)
line, = ax.plot([0,1], [-1,1], lw=2)
line1,=ax1.plot([0,1], [-1,1], lw=2)
tt = t[0]


forward_space = 0.5
backward_space = 0.1
diff_to_lead = 2
slider_limits = 5

# Insert slider
slider_ax = plt.axes([0.1, 0.1, 0.8, 0.02])
# Define sliders properties 
slider = Slider(slider_ax, "x_lim", -slider_limits, +slider_limits, valinit=0, color='#AAAAAA')



for i in range(0,1000):
    tt = np.append(tt,t[i])
    line.set_data(tt,np.sin(tt))
    line1.set_data(tt,np.cos(tt))
    if (max(tt)-min(tt) < diff_to_lead):
        ax.set_xlim(min(tt)-backward_space,diff_to_lead+forward_space)
        ax1.set_xlim(min(tt)-backward_space,diff_to_lead+forward_space)
    elif(np.mod(i,1)==0):
        def on_change(val):
            ax.set_xlim(max(tt)-diff_to_lead-backward_space-val, max(tt)+forward_space)
            ax1.set_xlim(max(tt)-diff_to_lead-backward_space-val, max(tt)+forward_space)
        slider.on_changed(on_change)
        ax.set_xlim(max(tt)-diff_to_lead-backward_space-slider.val, max(tt)+forward_space)
        ax1.set_xlim(max(tt)-diff_to_lead-backward_space-slider.val, max(tt)+forward_space)
    else:
        pass
    fig.canvas.draw()
    plt.pause(0.01)
    
   
