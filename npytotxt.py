import time
import sys
import os
import netCDF4 as nc4
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pickle
from matplotlib.dates import date2num, num2date
from matplotlib import dates
import subprocess
from datetime import datetime, timedelta

datanames = 5*['']
datanames[0] = '20180831105131_Grenzschichtentwicklung2_gps'
datanames[1] = '20180901095651_Grenzschichtentwicklung3_gps'
datanames[2] = '20180903132225_Grenzschichtentwicklung4_2_gps'
datanames[3] = '20180904124938_Grenzschichtentwicklung5_gps'
datanames[4] = '20180905094034_Grenzschichtentwicklung6_gps'


for i in range(len(datanames)):

    f = open(datanames[i] + '.txt', 'w')
    data = np.load('//192.168.206.173/lex2018/profil/Daten/'+datanames[i]+'.npy')
    f.write('Time in days since 01-01-0001 UTC;' +'Latitude;' + 'Longitude;' + 'Elevation' + '\n')
    for j in range(1,data.shape[0]):
        f.write(str(data[j,0])+';'+str(data[j,1])+';'+str(data[j,2])+';'+str(data[j,3])+'\n')
    f.close()

