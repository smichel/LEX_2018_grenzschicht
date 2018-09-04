import time
import netCDF4
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, num2date
from processing_functions import calc_pot_temp
import typhon
import datetime
dataFilePath = 'C:/Users/Uni/Desktop/CosmoDE/cd2_feh_2018090400.nc'
staticGridPath = 'C:/Users/Uni/Desktop/CosmoDE/cd2_feh_2018082900c.nc'
data = netCDF4.Dataset(dataFilePath)
staticGrid = netCDF4.Dataset(staticGridPath)
# Marienleuchte bei 11/10

landfraction = staticGrid.variables['FR_LAND'][:]
time = data.variables['time'][:]
timestring = data.variables['time'].units
date = datetime.datetime(int(data.variables['time'].units[12:16]),int(data.variables['time'].units[17:19]),int(data.variables['time'].units[20:22]),int(data.variables['time'].units[23:25]))
hhl = staticGrid.variables['HHL'][:]
heights = hhl[0,-17:-1,11,10]
P = data.variables['P'][:]
T = data.variables['T'][:]
T_2M = data.variables['T_2M'][:]
T_S = data.variables['T_S'][:]
Qv = data.variables['QV'][:]
RH = typhon.physics.vmr2relative_humidity(typhon.physics.specific_humidity2vmr(Qv), P*100, T)
U = data.variables['U'][:]
V = data.variables['V'][:]
W = data.variables['W'][:]
date = num2date(date2num(date) + time/24+2/24)
def cosmoprofil(variable): #nur für 1D und 2D sachen du otto
    if variable.ndim == 1:
        interpVariable = np.empty((len(variable)-1))
        for i in range(len(variable)-1):
            interpVariable[i]=0.5*(variable[i]+variable[i+1])
        return interpVariable
    elif variable.ndim == 2:
        interpVariable = np.empty((variable.shape[0],variable.shape[1]-1))
        for i in range(variable.shape[0]):
            for j in range(variable.shape[1]-1):
                interpVariable[i,j] = 0.5*(variable[i,j]+variable[i,j+1])
        return interpVariable
heights = cosmoprofil(heights)
pres = cosmoprofil(P[:,-17:-1,11,10]).T
Tprofile = cosmoprofil(T[:,-17:-1,11,10]).T
Tprofile = Tprofile-typhon.constants.zero_celsius

potT = calc_pot_temp(Tprofile, pres/100)
def plot_2d_timeseries(variable):
    f = plt.figure(frameon=True)
    ax = f.add_subplot(111)
    #for i in range(T.shape[0]):
    var1 = ax.imshow(variable)
    #ax.set_xticks(np.arange(0,16,2))
    ax.set_yticks(np.arange(0,16,2))
    ax.set_xticklabels(date[::4])
    plt.setp(plt.gca().xaxis.get_majorticklabels(),'rotation', 30)
    ax.set_yticklabels(np.round(heights[::2]))
    ax.set_xlabel('Date')
    ax.set_ylabel('Height in m')
    cb = plt.colorbar(var1)
    plt.show(block=False)
plot_2d_timeseries(potT-typhon.constants.zero_celsius)
plot_2d_timeseries((np.diff(potT,axis=0)*100)/np.diff(heights)[:,None])
plot_2d_timeseries(Tprofile)
print(1)