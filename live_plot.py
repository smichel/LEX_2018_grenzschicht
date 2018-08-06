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
from  matplotlib.dates import date2num
from matplotlib import dates
from datetime import datetime
import pickle
#import scipy
i = 0
t = 0
data_filename = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')
baud_rate = 9600
usb_port = '/dev/cu.wchusbserialfa130'
nslave = 10
plothistory = 600  # How much of the data should be plotted (in seconds)

data = {}
save_array = {}
f = open(data_filename+'.txt','w')

# Initialize figures and axes and lines
fig,[axtemp,axhum,axpres] = plt.subplots(3,1,figsize=(15,13))
jet = plt.get_cmap('gist_rainbow',nslave)

linestemp = {}
lineshum = {}
linespres = {}

fehlwert = -9999
for i in range(nslave):
    data[i+1] = np.zeros(4) + fehlwert
    save_array[i+1] = np.zeros(5)    + fehlwert 
    
    linestemp[i+1], = axtemp.plot_date([],[],linewidth=2,linestyle='-',marker=None,color=jet(i))
    lineshum[i+1], = axhum.plot_date([],[],linewidth=2,linestyle='-',marker=None,color=jet(i))
    linespres[i+1], = axpres.plot_date([],[],linewidth=2,linestyle='-',marker=None,color=jet(i))
    
xmin = date2num(datetime.now())
axtemp.set_ylabel('Temperature (Celsius)')
axtemp.set_title('Temperature')

axhum.set_ylabel('Humidity (%)')
axhum.set_title('Humidity')

axpres.set_xlabel('Time')
axpres.set_ylabel('Pressure (hPa)')
axpres.set_title('Pressure')

axtemp.grid(linestyle=':')
axhum.grid(linestyle=':')
axpres.grid(linestyle=':')

#set major ticks time format
axtemp.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
axhum.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
axpres.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))

timetxt = axtemp.text([], [],  [])

calib = [-0.478,1.112,-0.415,-0.861,-0.43,-0.367,-0.712,-0.257,0.346,-0.77]

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
            P = P + calib[int(name)-1]
            count = int(s[20:])
            s = 'Arduino ' + str(name) + ': ' + str(T) + ' '+ str(h)+ ' '+ str(P) + ' ' + str(count)
            print(s)
    
            data[name] = np.vstack((data[name],np.array([T,h,P,count])))
            f.write(str(datetime.now())+';'+str(name)+';'+str(T)+';'+str(h)+';'+str(P)+';'+str(count)+'\n') #maybe on other systems "" needs to be ''
            save_array[name] = np.vstack((save_array[name],np.array([date2num(datetime.now()),T,h,P,count])))
        except:
            print('NOPE...')
        if np.mod(i,40) == 0 and i > 50:
            time1 = time.time()
            print('SAVING...')
            f.close()
            f = open(data_filename+'.txt','a')
            with open(data_filename+'.npy','wb') as myFile:
                pickle.dump(save_array,myFile)
                myFile.close()

            # Set preliminary axes limits.
            timemin = max(xmin,save_array[1][-1,0]-plothistory/1e5) - 2e-5 # When plothistory is smaller than Inf, 
                                                                    # not everything is plotted, but only
                                                                    # the last plothistory seconds.
            timemax = save_array[1][-1,0] + 2e-5

            tempmin = 999
            tempmax = -999
            
            hummin = 999
            hummax = -999
            
            presmin = 9999
            presmax = -9999
            # PLOT
            for j in range(nslave):
                index = min(plothistory,len(save_array[j+1][:,0])-1)

                linestemp[j+1].set_data(save_array[j+1][1::,0],save_array[j+1][1::,1])
                lineshum[j+1].set_data(save_array[j+1][1::,0],save_array[j+1][1::,2])
                linespres[j+1].set_data(save_array[j+1][1::,0],save_array[j+1][1::,3])
                


                if min(save_array[j+1][-index::,1]) < tempmin +1:
                    tempmin = min(save_array[j+1][-index::,1]) - 1
                if max(save_array[j+1][-index::,1]) > tempmax -1:
                    tempmax = max(save_array[j+1][-index::,1]) + 1

                if min(save_array[j+1][-index::,2]) < hummin +1:
                    hummin = min(save_array[j+1][-index::,2]) - 1
                if max(save_array[j+1][-index::,2]) > hummax -1:
                    hummax = max(save_array[j+1][-index::,2]) + 1
                
                if min(save_array[j+1][-index::,3]) < presmin +1:
                    presmin = min(save_array[j+1][-index::,3]) - 1
                if max(save_array[j+1][-index::,3]) > presmax -1:
                    presmax = max(save_array[j+1][-index::,3]) + 1
                
                if max(save_array[j+1][-index::,0]) > timemax -2e-5:
                    timemax = max(save_array[j+1][-index::,0]) + 2e-5

                fig.canvas.flush_events()
             
            # Reset color cycle so that every arduino has the same color in the plot
            axtemp.set_prop_cycle(None)
            axhum.set_prop_cycle(None)
            axpres.set_prop_cycle(None)
            
            axtemp.set_ylim(tempmin,tempmax)
            axhum.set_ylim(hummin,hummax)
            axpres.set_ylim(presmin,presmax)

            axtemp.set_xlim(timemin,timemax)
            axhum.set_xlim(timemin,timemax)
            axpres.set_xlim(timemin,timemax)
            
            timetxt.set_position((timemin,tempmax+0.1))
            timetxt.set_text('Elapsed time: '+str(round(time.time()-time1,3))+' seconds!')

            axhum.legend((np.arange(nslave)+1).astype(str),loc='center left', bbox_to_anchor=(1, 0.5))
            plt.pause(0.01)

        

            
    t = t+1