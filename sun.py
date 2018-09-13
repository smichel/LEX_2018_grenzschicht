from pysolar.solar import *
import numpy as np
import datetime
from matplotlib.dates import date2num, num2date

dtype1=np.dtype([('Time','f8'),('Latitude','f8'),('Longitude','f8'),('Elevation','f8')])

data = np.loadtxt('/data/share/u231/u231101/lehre/lex2018/profil/Daten/Auslenkung_Leine/20180831105131_Grenzschichtentwicklung2_gps.txt',dtype=dtype1,skiprows=1,delimiter=';')

def strahlungsfehler(times, gott_file, base_location = (54.494849, 11.2400009)):
    '''



    :param times: input a date2num array
    :param gott_file: path to the gps file of gott
    :param base_location: can be changed, but is not needed
    :return: returns an array of booleans (with 1 = sunerror, 0 no sunerror or NAN for no gps data of gott) for each input timestep
    '''

    dtype1 = np.dtype([('Time', 'f8'), ('Latitude', 'f8'), ('Longitude', 'f8'), ('Elevation', 'f8')])

    data = np.loadtxt(gott_file,dtype=dtype1, skiprows=1, delimiter=';')
    sun_azi = np.zeros(len(data))
    gott_azi = np.zeros(len(data))

    intime = np.zeros(len(times))
    for i in range(len(times)):
        intime[i] = times[i]
    time = np.zeros(len(data))

    for i in range(len(data)):
        time[i] = data[i][0]
        sun_azimuth = get_azimuth(base_location[0], base_location[1], num2date(data[i][0]))
        gott_azi[i] = np.rad2deg(np.arctan2((base_location[0] - data[i][1]), (base_location[1] - data[i][2])))

        if sun_azimuth < 0:
            if (sun_azimuth >= -180):
                solarheading = ((sun_azimuth * -1) + 180)
            if (sun_azimuth < -180):
                solarheading = ((sun_azimuth * -1) - 180)
            if sun_azimuth >= 0:
                solarheading = sun_azimuth

        sun_azi[i] = solarheading

        if i > 0:
            if np.abs(gott_azi[i]-gott_azi[i-1])>1:
                gott_azi[i] = gott_azi[i-1]

    sun = np.zeros(len(data))
    sun[np.abs(sun_azi-gott_azi)<20] = 1

    idx = np.zeros(len(times))

    for i in range(len(intime)):
        idx[i] = np.argmax(intime[i]<time)

    sun_out = np.zeros(len(data))*np.nan

    for i in range(len(sun_out)):
        if idx[i] > 0:
            sun_out[i] = sun[idx[i]]

    return sun_out