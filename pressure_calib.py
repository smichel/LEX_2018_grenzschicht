#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 31 13:59:29 2018

@author: jf
"""
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
from matplotlib.dates import num2date, date2num
import datetime
#y =np.loadtxt('0731.txt',skiprows=1,usecols = (9),delimiter=';')

y = pd.read_csv('0731.txt',delimiter=';')
data = np.load('data.npy')
x=np.asarray(y)
x = x[769+15:,:]
### hieri st noch arbeit!!!
x_time = np.zeros(len(x))
for i in range(0,len(x_time)):
    x_time[i] =date2num(datetime.datetime(int(x[i][0][6:]),int(x[i][0][3:5]),int(x[i][0][0:2]),int(x[i][1][0:2]),int(x[i][1][3:5]),int(x[i][1][6:]))-datetime.timedelta(minutes=2,seconds=-4))
##hier ist alles wieder normal
start_value=369

start=np.zeros(10)
versatz=np.asarray([10,5,1,4,6,7,7,8,5,0])
arduino_data=10*['']
start[:]=start_value+versatz[:]

#dictionary indexed from 1-10
for i in range(1,11):
    arduino_data[i-1] = np.asarray(data[i])


start_druck = 16
versatz_referenz=440



######### finding values at same pressure level
def find_same_values(array,delta_p=0.2):
    mean_pressure_on_level = 0
    counter3 = 0
    counter4 = 0
    indices = 0
    level_counter = 0 #counts number of identified pressure levels
    value_counter1= 0 # counts value on a pressure level
    value_counter2= 0 #/ between pressure levels
    sum_of_values = 0 # sum of pressure values on same pressure level
    status        = 0 # 1 if on pressure level
    for i in range(0,len(array)-1):
#        print(i)
        if ((status == 0) and (value_counter2 == 1) and (sum_of_values != 0)):
            level_counter += 1
            if (np.max(mean_pressure_on_level) == 0):
                mean_pressure_on_level = sum_of_values/value_counter1
            else:
                mean_pressure_on_level = np.append(mean_pressure_on_level,sum_of_values/value_counter1)
        if array[i+1]-array[i]< delta_p:
            counter3 += 1
            if (counter3 == 1):
                indices = i
                indices = np.append(indices,i+1)
            else:
                indices = np.append(indices,i)
                indices = np.append(indices,i+1)
            value_counter2 = 0
            status = 1
            sum_of_values += array[i+1]
            value_counter1 += 1
        else:
            counter4 += 1
            if (counter4 == 1):
                indices2 = i
            else:
                indices2 = np.append(indices2,i)
            status = 0
            value_counter2 +=1
    indices = np.unique(indices)
    for v in indices:
        if v in indices2:
            pos = np.where(indices2 == v)
            indices2 = np.delete(indices2,pos)
    array2 = np.copy(array)
    array2[indices2]=np.nan
    return mean_pressure_on_level, indices,indices2, level_counter,array2

A,B,C,D,E = find_same_values(arduino_data[0][:,3][int(start[0]):],delta_p=0.25)
F,G,H,I,J = find_same_values(x[:,9],delta_p=0.25)

def level_indices(array,indices):
    level_indices = 15*['']
    sv = -1
    counter = 0
    for i in range(0,len(indices)-1):
        if indices[i+1]-indices[i]==1:
            counter += 1
            if (counter == 1):
                sv += 1
                level_indices[sv] = indices[i]
                level_indices[sv] = np.append(level_indices[sv],indices[i+1])
            else:
                level_indices[sv] = np.append(level_indices[sv],indices[i+1])
        else:
            counter = 0
    return level_indices
            
    
li = level_indices(J,G)

mean_values = 15*['']
maxmin_numpacks = 15*['']
arduino_indices = 10*[15*['']]
arduino_means = np.zeros([10,15])
difference_to_ref = np.zeros([10,15])

fig = plt.figure(figsize=(10,6))
ax = plt.subplot(221)
ax2=plt.subplot(222)
ax3=plt.subplot(224)

for i in range(0,10):
    ax.plot(arduino_data[i][:,0][int(start[i]):],arduino_data[i][:,3][int(start[i]):],label='arduino_'+str(i+1))
    ax2.plot(arduino_data[i][:,4][int(start[i]):],arduino_data[i][:,3][int(start[i]):],label='arduino_'+str(i+1))
   
    
xx = np.linspace(444,1348,len(x[:,9]))

for i in range (0,len(mean_values)):
    mean_values[i] = np.mean(x[:,9][li[i]])
    maxmin_numpacks[i] = [xx[li[i][0]],xx[li[i][-1]]]
    
def get_indices(l_b,u_b,lat,case='both'):
	#check if lower boundary is actually lower, and swap values if this is not the case
	if (l_b>u_b):
		l_b, u_b = u_b, l_b

	#calculate the indices
	if (case=='both'):
		indices1=np.where((lat>= -u_b) & (lat<= -l_b))
		indices2=np.where((lat>=l_b) & (lat <=u_b))
		indices = np.append(indices1,indices2)
	elif (case=='northern') or (case=='southern'):
		indices=np.where((lat>=l_b) & (lat<=u_b))
	else:
		print('specify the case variable "southern", "northern", or "both". E.g case=\'both\'') 
		indices=np.nan

	return indices

for i in range(0,10):
    for j in range(0,15):
        arduino_indices[i][j]=get_indices(maxmin_numpacks[j][0],maxmin_numpacks[j][1],arduino_data[i][:,4][int(start[i]):],case='northern')
        arduino_means[i][j] = np.mean(arduino_data[i][:,3][int(start[i]):][arduino_indices[i][j][0]])
        ax3.plot(arduino_data[i][:,4][int(start[i]):][arduino_indices[i][j][0]],arduino_data[i][:,3][int(start[i]):][arduino_indices[i][j][0]])
        length=len(arduino_data[i][:,4][int(start[i]):][arduino_indices[i][j][0]])
        #ax.plot(arduino_data[i][:,4][int(start[i]):][arduino_indices[i][j][0]],length*[arduino_means[i][j]])
        difference_to_ref[i][j] = mean_values[j] - arduino_means[i][j]




ax.plot(x_time,x[:,9],label='reference',linewidth=1,alpha=1,color='k')
ax2.plot(xx[:],x[:,9],label='reference',linewidth=1,alpha=1,color='k')
ax3.plot(xx[:],x[:,9],label='reference',linewidth=3,alpha=0.4,color='c')

ax3.plot(xx[:],J,alpha = 1,color='k',label='used for calib')
ax.set_ylim(850,1010)
ax2.set_ylim(961,966)
ax2.set_xlim(1042,1114)
ax3.set_ylim(961,966)
ax3.set_xlim(1042,1114)
ax.set_xlabel('packetnum')
ax.set_ylabel('pressure [hPa]')
ax3.set_ylabel('pressure [hPa]')
ax2.set_xlabel('packetnum')
ax.grid(linestyle='--',alpha=0.4)
ax.legend(bbox_to_anchor=(0.3, -0.09))   
ax3.legend(bbox_to_anchor=(-0.2, 0.5))  
fig.savefig('1.png',dpi=500) 

fig2 = plt.figure(figsize=(10,6))
ax4 = plt.subplot(111)


for i in range(0,10):
    ax4.plot(difference_to_ref[i],mean_values,'x',linestyle='-',label='arduino_'+str(i+1))     
    ax4.plot((len(mean_values))*[np.mean(difference_to_ref[i][1:-1])], mean_values,color='k',linestyle ='--',alpha=0.5)

    
ax4.grid(alpha=0.4)
ax4.set_ylabel('reference height [hPa]')
ax4.set_xlabel('deviation to ref [hPa]')
ax4.legend()       
fig2.savefig('2.png',dpi=500) 
dtr = difference_to_ref

for i in range(0,10):
    for j in range(0,15):
        dtr[i][j]=np.round(dtr[i][j],decimals=3)

with open('names.csv', 'w', newline='') as csvfile:
    fieldnames = ['ref', '1','2','3','4','5','6','7','8','9','10']
    writer = csv.DictWriter(csvfile,fieldnames=fieldnames)

    writer.writeheader()
    for i in range(0,len(mean_values)):
        writer.writerow({'ref':np.round(mean_values[i],decimals=3), '1':dtr[0][i],'2':dtr[1][i],'3':dtr[2][i],'4':dtr[3][i],'5':dtr[4][i],'6':dtr[5][i],'7':dtr[6][i],'8':dtr[7][i],'9':dtr[8][i],'10':dtr[9][i]})
        
    writer.writerow({'ref': 'mean', '1':np.round(np.mean(dtr[0][:-1]),decimals=3),'2':np.round(np.mean(dtr[1][:-1]),decimals=3),'3':np.round(np.mean(dtr[2][:-1]),decimals=3),'4':np.round(np.mean(dtr[3][:-1]),decimals=3),'5':np.round(np.mean(dtr[4][:-1]),decimals=3),'6':np.round(np.mean(dtr[5][:-1]),decimals=3),'7':np.round(np.mean(dtr[6][:-1]),decimals=3),'8':np.round(np.mean(dtr[7][:-1]),decimals=3),'9':np.round(np.mean(dtr[8][:-1]),decimals=3),'10':np.round(np.mean(dtr[9][:-1]),decimals=3)})
    
fig5 = plt.figure(figsize=(10,6))
ax7 = plt.subplot(111)
for i in range(0,10):
    ax7.scatter(mean_values,arduino_means[i],label=str(i+1),s=5,marker='x')
    
ax7.set_aspect('equal')
ax7.plot([860,1010],[860,1010],linestyle='--',color='k')
ax7.set_xlim(860,1010)
ax7.set_ylim(860,1010)
ax7.legend()