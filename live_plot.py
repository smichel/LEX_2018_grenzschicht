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
from matplotlib.dates import date2num
from matplotlib import dates
from datetime import datetime
import pickle
#22,73

data_filename = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')
data_filename = data_filename + '_Grenzschichtentwicklung'
baud_rate = 115200
usb_port = '/dev/cu.wchusbserial1420'
slaves = np.array([1,2,3,4,5,6,7,8,9,10,11]) -1
first = slaves[0] + 1
plothistory = 10000  # How much of the data should be plotted (in seconds)

data = {}
save_array = {}
f = open(data_filename+'.txt','w')

nslave = len(slaves)
halfslave = int(11/2)+1
# Initialize figures and axes and lines
fig,[axtemp,axhum,axpres] = plt.subplots(3,1,figsize=(10,13))
jet = plt.get_cmap('gist_rainbow',int(halfslave))

linestemp = {}
lineshum = {}
linespres = {}

fehlwert = -9999
for i in slaves:
    data[i+1] = np.zeros(4) + fehlwert
    save_array[i+1] = np.zeros(5)    + fehlwert 
    
    cindex = np.mod(i,halfslave)
    if i+1 > halfslave:
        stylus = '--'
    else:
        stylus = '-'
        
    linestemp[i+1], = axtemp.plot_date([],[],linewidth=2,linestyle=stylus,marker=None,color=jet(cindex))
    lineshum[i+1], = axhum.plot_date([],[],linewidth=2,linestyle=stylus,marker=None,color=jet(cindex))
    linespres[i+1], = axpres.plot_date([],[],linewidth=2,linestyle=stylus,marker=None,color=jet(cindex))

gott = np.zeros(4)+fehlwert

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


Pcalib = [-0.478,1.112,-0.415,-0.861,-0.43,-0.367,-0.712,-0.257,0.346,-0.77,-0.8]
#Hcalib = [2.6967455282278791, 2.019810301232212, 0.7988041850625507, 0.33789509780086746, 1.4866460360382234, -1.4921282077773412, -2.214225778675157, 0.7299801435411979, -3.2266263048570636, -0.31907172948442053]
#Tcalib = [-0.20298338235838642, -0.03457388306773623, -0.14143909679448186, -0.21896698336938059, -0.31915655917819663, 0.27426237148132415, 0.17265320130558948, 0.1972397629378655, 0.14218800363267192, 0.13077656541075555]
# Calibration auf Lüftung:
Tcalib = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
#Tcalib = [-0.38750000000001705, -0.2830645161290377, -0.5447580645161523, -0.6460000000000186, -0.4228346456693082, -0.36373983739838067, -0.320960000000035, -0.3742148760330828, -0.5042975206611935, -0.35826771653544043]
#Hcalib = [0.03306371769425098, 0.13749920156523032, -0.12419434682188424, -0.22543628230575052, -0.002270927975040138, 0.05682388029588736, 0.09960371769423304, 0.04634884166118525, -0.08373380296692545, 0.06229600115882761]

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
            # Set preliminary axes limits.
            timemin = max(xmin,save_array[first][-1,0]-plothistory/1e5) - 2e-5 # When plothistory is smaller than Inf, 
                                                                    # not everything is plotted, but only
                                                                    # the last plothistory seconds.
            timemax = save_array[first][-1,0] + 2e-5

            tempmin = 999
            tempmax = -999
            
            hummin = 999
            hummax = -999
            
            presmin = 9999
            presmax = -9999
            # PLOT
            for j in slaves:
                index = min(int(plothistory*4/nslave),len(save_array[j+1][:,0])-1)

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
            
            axtemp.set_ylim(tempmin,tempmax)
            axhum.set_ylim(hummin,hummax)
            axpres.set_ylim(presmin,presmax)

            axtemp.set_xlim(timemin,timemax)
            axhum.set_xlim(timemin,timemax)
            axpres.set_xlim(timemin,timemax)
            
            timetxt.set_position((timemin,tempmax+0.1))
            timetxt.set_text('Elapsed time: '+str(round(time.time()-time1,3))+' seconds!')

            axhum.legend((slaves+1).astype(str),loc='center left', bbox_to_anchor=(1, 0.5))
            plt.pause(0.01)
            # Save image and convert to JPG
            if (np.mod(i,400)==0):
                fig.savefig('live.png')


            
    t = t+1