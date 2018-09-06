import time
import netCDF4
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, num2date
from processing_functions import calc_pot_temp, calc_pseudopot_temp
import typhon
import datetime

class cosmoData:

    def __init__(self, dataFilePath,staticGridPath='//192.168.206.173/lex2018/profil/Daten/Cosmo/cd2_feh_2018082900c.nc', maxlevel = -22):
        #self.dataFilePath = 'C:/Users/Uni/Desktop/CosmoDE/cd2_feh_2018090400.nc'
        #alpaca = np.load('//192.168.206.173/lex2018/profil/Daten/20180904124938_Grenzschichtentwicklung5.npy')

        #staticGridPath = '//192.168.206.173/lex2018/profil/Daten/Cosmo/cd2_feh_2018082900c.nc'
        self.data = netCDF4.Dataset(dataFilePath)
        self.staticGrid = netCDF4.Dataset(staticGridPath)
    # Marienleuchte bei 11/10
        self.maxlevel = maxlevel
        self.landfraction = self.staticGrid.variables['FR_LAND'][:]
        self.time = self.data.variables['time'][:]
        self.timestring = self.data.variables['time'].units
        self.date = datetime.datetime(int(self.timestring[12:16]),int(self.timestring[17:19]),int(self.timestring[20:22]),int(self.timestring[23:25]))
        self.hhl = self.staticGrid.variables['HHL'][:]
        self.heights = self.hhl[0,maxlevel:-1,11,10]
        self.P = self.data.variables['P'][:]
        self.T = self.data.variables['T'][:]
        self.T_2M = self.data.variables['T_2M'][:]
        self.T_S = self.data.variables['T_S'][:]
        self.Qv = self.data.variables['QV'][:]
        self.RH = typhon.physics.vmr2relative_humidity(typhon.physics.specific_humidity2vmr(self.Qv), self.P*100, self.T)
        self.U = self.data.variables['U'][:]
        self.V = self.data.variables['V'][:]
        self.W = self.data.variables['W'][:]
        self.date = num2date(date2num(self.date) + self.time/24+2/24)
        self.heights = cosmoprofil(self.heights)

    def get_bnd_layers(self):
        """
        get bnd layers gives back the layer
        """
        self.pseudoPotTemp = calc_pseudopot_temp(cosmoprofil(self.RH[:, self.maxlevel:-1, 11, 10]),
                                                 cosmoprofil(self.T[:, self.maxlevel:-1, 11, 10])
                                                 - typhon.constants.zero_celsius,
                                                 cosmoprofil(self.P[:, self.maxlevel:-1, 11,
                                                             10]) / 100) - typhon.constants.zero_celsius

        self.potT = calc_pot_temp(cosmoprofil(self.T[:, self.maxlevel:-1, 11, 10])
                                  - typhon.constants.zero_celsius,
                                  cosmoprofil(self.P[:, self.maxlevel:-1, 11, 10]) / 100)

        self.RHslice = cosmoprofil(self.RH[:,self.maxlevel:-1,11,10])
        self.Qvslice = cosmoprofil(self.Qv[:,self.maxlevel:-1,11,10])
        potT_bnd = self.heights[np.argmin((np.diff(self.potT[:,:-2],axis=1)*100)/np.diff(self.heights)[None,:-2],axis=1)]
        pseudoPotT_bnd = self.heights[np.argmax((np.diff(self.pseudoPotTemp, axis=1) * 100) / np.diff(self.heights)[None, :], axis=1)]
        relH_bnd = self.heights[np.argmax((np.diff(self.RHslice, axis=1) * 100) / np.diff(self.heights)[None, :], axis=1)]
        QV_bnd = self.heights[np.argmax((np.diff(self.Qvslice, axis=1) * 100) / np.diff(self.heights)[None, :], axis=1)]

        return potT_bnd,pseudoPotT_bnd,relH_bnd,QV_bnd

    def plot_2d_timeseries(self,variable,caxismin=None, caxismax=None):
        if caxismin == None:
            caxismin = np.floor(np.min(variable))
        if caxismax == None:
            caxismax = np.ceil(np.max(variable))

        f = plt.figure(frameon=True)
        ax = f.add_subplot(111)
        #for i in range(T.shape[0]):
        var1 = ax.imshow(variable,vmin=caxismin,vmax=caxismax)
        #ax.set_xticks(np.arange(0,16,2))
        ax.set_yticks(np.arange(0,variable.shape[0],2))
        ax.set_xticklabels(self.date[::4])
        plt.setp(plt.gca().xaxis.get_majorticklabels(),'rotation', 30)
        ax.set_yticklabels(np.round(self.heights[::2]))
        ax.set_xlabel('Date')
        ax.set_ylabel('Height in m')
        cb = plt.colorbar(var1)#,boundaries=np.arange(caxismin,caxismax,(caxismax-caxismin)/10))
        plt.show(block=False)

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



# day1 = cosmoData('C:/Users/Uni/Desktop/CosmoDE/cd2_feh_2018090400.nc','C:/Users/Uni/Desktop/CosmoDE/cd2_feh_2018082900c.nc')
# potT_bnd,pseudoPotT_bnd,relH_bnd,Qv_bnd = day1.get_bnd_layers()

# plt.figure()
# plt.contourf(day1.time, day1.heights[1:], np.diff(day1.potT,axis=1).T)
# plt.plot(potT_bnd)
# plt.colorbar()
# plt.title('PotT')
# plt.ylim((0,np.max(day1.heights[1:])))
# plt.show(block=False)
#
# plt.figure()
# plt.contourf(day1.time, day1.heights[1:], np.diff(day1.pseudoPotTemp.T,axis=0))
# plt.plot(pseudoPotT_bnd)
# plt.colorbar()
# plt.title('PseudoPotT')
# plt.ylim((0,np.max(day1.heights[1:])))
# plt.show(block=False)
#
# plt.figure()
# plt.contourf(day1.time, day1.heights[1:], np.diff(cosmoprofil(day1.RH[:, day1.maxlevel:-1, 11, 10]).T,axis=0))
# plt.plot(relH_bnd)
# plt.colorbar()
# plt.title('RH')
# plt.ylim((0,np.max(day1.heights[1:])))
# plt.show(block=False)
#
# plt.figure()
# plt.contourf(day1.time, day1.heights[1:], np.diff(cosmoprofil(day1.Qv[:, day1.maxlevel:-1, 11, 10]).T,axis=0))
# plt.plot(Qv_bnd)
# plt.colorbar()
# plt.title('Qv')
# plt.ylim((0,np.max(day1.heights[1:])))
# plt.show(block=False)
