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
from processing_functions import apply_correction
import subprocess
from datetime import datetime, timedelta
def profildata(data, time_start, time_end):
    """
    Plots vertica profiles of temperature and humidty for a given time period.

    Parameters:
        data (dictionary): dictionary with data for all alpacas
        time_start (datetime.datetime(yyyy, mm, dd, HH, MM, SS)): start time of
            time period
        time_end (datetime.datetime(yyyy, mm, dd, HH, MM, SS)): end time of
            time period
    """
    plt.rcParams.update({'font.size': 14})

    temp = {}
    hum = {}
    pres = {}
    for alpaca in data:
        temp[alpaca] = data[alpaca][
            np.logical_and(data[alpaca][:, 0] >= date2num(time_start), data[alpaca][:, 0] <= date2num(time_end)), 1]
        hum[alpaca] = data[alpaca][
            np.logical_and(data[alpaca][:, 0] >= date2num(time_start), data[alpaca][:, 0] <= date2num(time_end)), 2]
        pres[alpaca] = data[alpaca][
            np.logical_and(data[alpaca][:, 0] >= date2num(time_start), data[alpaca][:, 0] <= date2num(time_end)), 3]
        if len(temp[alpaca]) == 0:
            temp[alpaca] = np.array([data[alpaca][data[alpaca][:, 0] >= date2num(time_start), 1][0]])
            hum[alpaca] = np.array([data[alpaca][data[alpaca][:, 0] >= date2num(time_start), 2][0]])
            pres[alpaca] = np.array([data[alpaca][data[alpaca][:, 0] >= date2num(time_start), 3][0]])
        #print('Arduino {}: Number of averaged timesteps: {}'.format(alpaca, len(temp[alpaca])))
        temp[alpaca] = np.mean(temp[alpaca])
        hum[alpaca] = np.mean(hum[alpaca])
        pres[alpaca] = np.mean(pres[alpaca])

    return temp,hum,pres
def altitude(pressure, temperature, z0):
    """ Calculates altitude fromm pressure and temperature.

    Parameters:
        pressure (array): vertical pressure profile
        temperature (array): vertical temperature profile
        z0 (numeric): altitude of ground pressure level
    """

    if np.sum(np.logical_not(np.isnan(temperature))) <= 1:
        return temperature
    # constants
    R = 287.058
    g = 9.81

    temperature = temperature + 273.15
    temp_notnan = temperature[np.logical_not(np.isnan(temperature))]
    # print(temp_notnan)
    pres_notnan = pressure[np.logical_not(np.isnan(temperature))]
    # print(pres_notnan)
    z = np.zeros(len(pres_notnan))
    z_interv = np.zeros(len(pres_notnan))

    for lev in range(0, len(pres_notnan) - 1):
        z_interv[lev + 1] = np.log(pres_notnan[lev + 1] / pres_notnan[lev]) * -(
                    R * (temp_notnan[lev] + temp_notnan[lev + 1]) / 2 / g)

        z[lev + 1] = np.sum(z_interv)

    z = z + z0
    # print(z)

    z_nan = np.zeros(temperature.shape)
    i = 0
    for lev in range(len(temperature)):
        if np.isnan(temperature[lev]):
            z_nan[lev] = np.nan
        else:
            z_nan[lev] = z[i]
            i += 1

    return z_nan

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).seconds)):
        yield start_date + timedelta(n*60)


def tether(zeit,data,i):
    if len(data) == 12:
        del data[12]
    T, H, P = profildata(data, num2date(zeit), num2date(zeit))
    Z = altitude(np.asarray(list(P.values())), np.asarray(list(T.values())), 7)
    deltaZ = np.diff(Z)
    deltaL = np.diff(lengths[i])
    deltaX = np.sqrt(deltaL ** 2 - deltaZ ** 2)
    X = np.cumsum(deltaX)
    X = np.append(0,X)
    return X,Z

datanames = 6*['']
datanames[0]=  '20180829062417_Grenzschichtentwicklung1'
datanames[1] = '20180831105131_Grenzschichtentwicklung2'
datanames[2] = '20180901095651_Grenzschichtentwicklung3'
datanames[3] = '20180903132225_Grenzschichtentwicklung4_2'
datanames[4] = '20180904124938_Grenzschichtentwicklung5'
datanames[5] = '20180905094034_Grenzschichtentwicklung6'

lengths=6*['']
lengths[0] = np.array((2,52,152,252,352,452,552,652,752,852,952))
lengths[1] = np.array((3,53,153,253,353,453,553,653,753,853,950))
lengths[2]= np.array((2,100,200,300,400,500,600,700,800,900,1000))
lengths[3] = np.array((4,100,200,300,400,500,600,700,820,900,1000))
lengths[4] = np.array((4,100,200,300,400,500,600,700,820,900,1000))
lengths[5] = np.array((4,100,200,300,400,500,600,700,820,900,1000))

#dataname = '20180831105131_Grenzschichtentwicklung2'
for i in range(len(datanames)):
    data = np.load('//192.168.206.173/lex2018/profil/Daten/'+datanames[i]+'.npy')
    data = apply_correction(data)
    einzelschitt = np.load('C:/Users/Uni/LEX_2018_grenzschicht/Messdaten/einzelanschnitt.npy')



    X_displacement = np.zeros(11)
    Z_displacement = np.zeros(11)
    Time = data[1][1,0]

    for zeit in data[1][1:,0]:
        try:
            Xdummy, Zdummy= tether(zeit,data,i)
            Time = np.append(Time, zeit)
            X_displacement = np.vstack((X_displacement,Xdummy))
            Z_displacement = np.vstack((Z_displacement,Zdummy))
            #f.write(str(zeit) + ';' + str(Xdummy) + ';' + str(Zdummy)+'\n')  # maybe on other systems "" needs to be ''

        except:
            print('error')

    f = nc4.Dataset(datanames[i]+'_tether.nc', 'w', format='NETCDF4')  # 'w' stands for write
    tempgrp = f.createGroup('Tether_data')
    tempgrp.createDimension('time', len(Time))
    tempgrp.createDimension('alpaca_number', X_displacement.shape[1])

    TIME = tempgrp.createVariable('Time', 'f4', 'time')
    Alapca_number = tempgrp.createVariable('Alpaca_number', 'i4', 'alpaca_number')
    X_DISPLACEMENT = tempgrp.createVariable('X_displacement', 'f4', ('alpaca_number','time'))
    Z_DISPLACEMENT = tempgrp.createVariable('Z_displacement', 'f4', ('alpaca_number','time'))
    Time[:] = Time
    X_DISPLACEMENT[:,:] = X_displacement
    Z_DISPLACEMENT[:,:] = Z_displacement

    np.savez(datanames[i] + '_displacements.npz', X_displacement, Z_displacement, Time)

    #text_file = np.savetxt(datanames[i]+'_displacements.txt',(Time,X_displacement,Z_displacement),fmt='%.18g', delimiter=' ', newline=os.linesep)
