import time
import sys
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib.dates import date2num, num2date
from matplotlib import dates
import subprocess
from datetime import datetime, timedelta
def profilplot(data, time_start, time_end):
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


data = np.load('//192.168.206.173/lex2018/profil/Daten/20180829062417_Grenzschichtentwicklung.npy')
einzelschitt = np.load('C:/Users/Uni/LEX_2018_grenzschicht/Messdaten/einzelanschnitt.npy')
length_1 = np.array((2,52,152,252,352,452,552,652,752,852,952))
length_2 = np.array((3,53,153,253,353,453,553,653,753,853,950))
length_3 = np.array((2,100,200,300,400,500,600,700,800,900,1000))

f = plt.figure(frameon = True, figsize=(5, 5))
canvas_width, canvas_height = f.canvas.get_width_height()
ax = f.add_subplot(111)

#ax = f.add_axes([0, 0, 1, 1])
line, = ax.plot([],[])
ax.set_xlim([0,900])
ax.set_ylim([0,900])
ax.set_xlabel('Auslenkung am Boden in m')
ax.set_ylabel('Höhe in m')
def update(zeit,data):
    T, H, P = profilplot(data, num2date(zeit), num2date(zeit))
    Z = altitude(np.asarray(list(P.values())), np.asarray(list(T.values())), 7)
    deltaZ = np.diff(Z)
    deltaL = np.diff(length_1)
    deltaX = np.sqrt(deltaL ** 2 - deltaZ ** 2)
    X = np.cumsum(deltaX)
    X = np.append(0,X)
    Z = np.append(0,Z)

    line.set_data(X[1:], Z[2:])
    plt.title(num2date(zeit))
    plt.pause(0.00001)
    #plt.show(block=False)

# Open an ffmpeg process
outf = 'Aufstieg1.mp4'
cmdstring = ('ffmpeg',
    '-y', '-r', '30', # overwrite, 30fps
    '-s', '%dx%d' % (canvas_width, canvas_height), # size of image string
    '-pix_fmt', 'argb', # format
    '-f', 'rawvideo',  '-i', '-', # tell ffmpeg to expect raw video from the pipe
    '-vcodec', 'mpeg4', outf) # output encoding
p = subprocess.Popen(cmdstring, stdin=subprocess.PIPE)

# Draw 1000 frames and write to the pipe
for zeit in data[1][1::2,0]:
    # draw the frame
    update(zeit,data)
    plt.draw()

    # extract the image as an ARGB string
    string = f.canvas.tostring_argb()

    # write to pipe
    p.stdin.write(string)

# Finish up
print(num2date(zeit))
p.communicate()