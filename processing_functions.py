 
import sys
import numpy as np
from scipy.interpolate import interp1d
from matplotlib.dates import date2num, num2date
import datetime
import pickle
import typhon
###############################################################################
###############################################################################
""" This is a list of functions used for processing the measurement data. 
It includes calibration, Time- and Pressure interpolation and a calculation of
the height from pressure.
"""
###############################################################################
###############################################################################
def read_data(path,filename):
    file=path+filename
    data = np.load(path + filename)
    print("read: ",file)
    return data;
###############################################################################
#def time_cut_data(data):
#       
#
#
#
###############################################################################
def apply_correction(data):
    """ Applies temperature and humidity correction to ALPACA raw data and 
    returns a dictionary with the same structure as in the raw data, but 
    with the corrected values. 
    """
    
    
    arduinos = data.keys()
    
    temp_correction = {1: 0.09, 2: 0.10, 3: -0.02, 4: -0.23, 5: -0.20,
                       6: 0.05, 7: 0.15, 8: 0.12, 9: -0.10, 10: 0.11,
                       11: 0.0}#-0.08}
    temp_bias = 0.4896611061095239
    
    humidity_correction = {1: -0.15, 2: 0.28, 3: -0.09, 4: 0.08, 5: 0.41,
                       6: -0.19, 7: -2.16, 8: 1.01, 9: -0.64, 10: -0.35,
                       11: 0.0}#2.01}
    humidity_bias = 2.7331455153884265
    
    pressure_correction = {1: -0.478, 2: 1.112, 3: -0.415, 4: -0.861, 5: -0.43,
                       6: -0.367, 7: -0.712, 8: -0.257, 9: 0.346, 10: -0.77,
                       11: 0.0}
    pressure_bias = 1.213813881674857
    
    for i in arduinos:
        # temperature
        data[i][1:, 1] = data[i][1:, 1] + temp_correction[i] - temp_bias
        # humidity
        data[i][1:, 2] = data[i][1:, 2] + humidity_correction[i] - humidity_bias
    print("Temperature and humidity calibrated")

    if data[1][1, 0] > date2num(datetime.datetime(2018, 8, 31, 0, 0)):
        for i in arduinos:
            # pressure
            data[i][1:, 3] = data[i][1:, 3] + pressure_correction[i] -pressure_bias
        print("Pressure calibrated")
                
    return data
###############################################################################
###############################################################################
def get_gradients(unit_time,p_levels,Temp_pint,Theta,RH_pint):
    p_mid_levels=[]
    for p in range(0,len(p_levels)-1):
        p_mid_levels.append((p_levels[p+1]+p_levels[p])/2)
    Temp_diff=np.diff(Temp_pint,axis=0)
    Theta_diff=np.diff(Theta,axis=0)
    RH_diff=np.diff(RH_pint,axis=0)
    print("Gradients calculated")
    return p_mid_levels,Temp_diff,Theta_diff,RH_diff;
###############################################################################
###############################################################################

def data_interpolation_p_t(data,ref,p_intv_no,instrument_spef):
    """ file is the filename joined with path.
        instrument_spef is 0 for Alpacas.
        p_intv_no is the number of desired p_levels for Arduinos
    """
    c_p=1005 #J/(kg*K)
    R_l=287  #J/(kg*K)
    
    if instrument_spef == 0:
        #data=np.load(file)
        keys=list(data)
        arduino={}
        unit_time=data[keys[ref]][1:,0]
        key_idx= np.asarray(keys)        #ard_number=np.array([1,2,3,4,5,6,7,8,9,10,11])
        interp_data=np.zeros([len(key_idx),4,len(unit_time)])
    
        for i in range(0,len(keys)):
            for j in range(0,4): # 0 Time, 1 Temp, 2 RH, 3 
                arduino[keys[i]]=np.asarray(data[keys[i]])
                interp_data[i,j,:]= interp1d(arduino[keys[i]][1::,0],arduino[keys[i]][1::,j],axis=0,fill_value='extrapolate')(unit_time)
        print("Data time interpolated")
    
        p_min=interp_data[:,3,:].min()
        p_max=interp_data[:,3,:].max()
        p_levels=np.linspace(p_min,p_max,p_intv_no)
        pres_interp=np.zeros([len(p_levels),4,len(unit_time)])
        for t in range(0,len(unit_time)):
            for j in range(0,3):
                    pres_interp[:,j,t]=interp1d(interp_data[::,3,t],interp_data[::,j,t],axis=0,fill_value=np.nan,bounds_error=False)(p_levels)
        print("Data p-interpolated")
    
        Temp_pint=pres_interp[:,1,:]
        RH_pint=pres_interp[:,2,:]
    
        #Pot. Temperatur
        Theta = np.empty((p_intv_no,len(unit_time),))
        Theta.fill(np.nan)
        for t in range(0,len(unit_time)):
            for p in range(0,len(p_levels)):
                Theta[p,t]=(Temp_pint[p,t]+273.15)*(1000/p_levels[p])**(R_l/c_p)
        return unit_time,p_levels,Temp_pint,RH_pint,Theta
    elif instrument_spef ==1:
        print("Processing of LIDAR data")
        if np.size(p_intv_no) > 1: 
            p_levels= p_intv_no
        else:
            print('Error: if you want interpolate LIDAR/Radiosonde data, you need to insert the p_levels (from Arduino) for the argument p_intv_no')
            sys.exit()
        return None
        
    elif instrument_spef ==2:
        print('Processing of Radiosonde data')
        if np.size(p_intv_no) > 1: 
            p_levels= p_intv_no
        else:
            print('Error: if you want interpolate LIDAR/Radiosonde data, you need to insert the p_levels (from Arduino) for the argument p_intv_no')
            sys.exit()
        return None


###############################################################################
###############################################################################
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
    #print(temp_notnan)
    pres_notnan = pressure[np.logical_not(np.isnan(temperature))]
    #print(pres_notnan)
    z = np.zeros(len(pres_notnan))
    z_interv = np.zeros(len(pres_notnan))

    for lev in range(0, len(pres_notnan)-1):
        z_interv[lev+1] = np.log(pres_notnan[lev+1] / pres_notnan[lev]) * -(R * (temp_notnan[lev] + temp_notnan[lev+1]) / 2 / g)
        
        z[lev+1] = np.sum(z_interv)
       
    z = z + z0
    #print(z) 
    
    z_nan = np.zeros(temperature.shape)
    i = 0
    for lev in range(len(temperature)):
        if np.isnan(temperature[lev]):
            z_nan[lev] = np.nan
        else: 
            z_nan[lev] = z[i]
            i += 1
    
    return z_nan

def calc_specific_humidity(rh, temperature, pressure):
    """ Calculates specific humidity.
    """
    temperature = temperature + 273.15
    pressure = pressure * 100
    rh = rh / 100
    eq_vapour_pres = typhon.physics.e_eq_water_mk(temperature)
    vapour_pres = eq_vapour_pres * rh
    vmr = vapour_pres / pressure
    specific_hum = typhon.physics.vmr2specific_humidity(vmr)
    
    return specific_hum

def calc_mass_mixing_ratio(rh, temperature, pressure):
    """ Calculates mass mixing ratio. 
    
    Parameters:
        rh (array): relative humidity in %
        temperature (array): temperature in °C
        pressure (array): pressure in hPa
    """
    temperature = temperature + 273.15
    pressure = pressure * 100
    rh = rh / 100
    eq_vapour_pres = typhon.physics.e_eq_water_mk(temperature)
    vapour_pres = eq_vapour_pres * rh
    vmr = vapour_pres / pressure
    
    return typhon.physics.vmr2mixing_ratio(vmr)

def calc_pot_temp(temperature, pressure):
    """ Calculates potential temperature in KELVIN!!!
    
    Parameters:
        temperature (array): temperature in °C
        pressure (array): pressure in hPa
    """
    c_p = typhon.constants.isobaric_mass_heat_capacity
    R_l = typhon.constants.gas_constant_dry_air
    temperature = temperature + 273.15
    pressure = pressure * 100
    
    return temperature*(100000/pressure)**(R_l/c_p)

def calc_pseudopot_temp(rh, temperature, pressure):
    """ Calculates pseudopotential temperatuer in Kelvin.
    
    Parameters:
        rh (array): relative humidity in %
        temperature (array): temperature in °C
        pressure (array): pressure in hPa
    """
    cp = typhon.constants.isobaric_mass_heat_capacity
    L = typhon.constants.heat_of_vaporization
    mixing_ratio = calc_mass_mixing_ratio(rh, temperature, pressure)
    pot_temp = calc_pot_temp(temperature, pressure)
    temperature = temperature + 273.15
    pressure = pressure * 100
    rh = rh / 100

    pseudopot_temp = pot_temp * np.exp(L * mixing_ratio / cp / temperature)
    
    return pseudopot_temp

def calc_virt_pot(rh, temperature, pressure):
    """ Calculates virtual potential temperatuer in Kelvin.
    
    Parameters:
        rh (array): relative humidity in %
        temperature (array): temperature in °C !!!
        pressure (array): pressure in hPa
    """
    specific_humidity = calc_specific_humidity(rh, temperature, pressure)
    virt_temperature = ((temperature + 273.15) * (1 + 0.6078*specific_humidity)) - 273.15
    virtpot_temp = calc_pot_temp(virt_temperature, pressure)
    
    return virtpot_temp

def calc_bulk_richardson(virtpot_temp, windspeed_hor, altitudes):
    """ Calculates Bulk Richardson number from fields of virtual potential temperature,
    horizontal windspeed and the corresponding altitude levels.
    """
    g = 9.81
    
    Ri = np.zeros(windspeed_hor.shape)
    
    for i in range(windspeed_hor.shape[1]):
        if np.any(np.logical_not(np.isnan(virtpot_temp[:, i]))):
            idx = np.nonzero(np.logical_not(np.isnan(virtpot_temp[:, i])))[0][-1]
        else:
            idx = 0
        Ri[:, i] = g * altitudes[:, i] * (virtpot_temp[:, i] - virtpot_temp[idx, i]) / (virtpot_temp[:, i] * windspeed_hor[:, i])
    
    return Ri

def boundary_layer_height(RH_pint, Temp_pint, p_levels, crit_variable):
    """
    This is a function to find the boundary layer height, based on gradients of
    the crit_variable( e.g. Theta, RH, specific humidity)   
    
    Parameters:
        RH_pint (array): relative humidity in % interpolated on fixed pressure levels
        Temp_pint (array): temperature in K interpolated on fixed pressure levels
        p_levels (2darray): pressure levels RH_pint and Temp_pint are interpolated on
        crit_variable (str): Variable that should be used to determine the 
            boundary layer height. Possibilities are 'relave_humidity', 
            'specific_humidity', 'potential_temperature' and 'pseudopotential_temperature'
    """
    # calculate altitudes
    crit_variable = crit_variable.lower()
    len_timeseries = Temp_pint.shape[1]
    num_plevels = p_levels.shape[0]
    
    z_levels = np.zeros(Temp_pint.shape)
    if crit_variable == 'relative_humidity':
        variable_diff = np.diff(RH_pint, axis=0) / np.diff(p_levels, axis=0)
        variable_diff[np.isnan(variable_diff)] = -9999
        diff_extreme_idx = np.nanargmax(variable_diff[int(num_plevels/10):-int(num_plevels/4)], axis=0)+int(num_plevels/10)
    elif crit_variable == 'specific_humidity':
        specific_humidity = calc_specific_humidity(RH_pint, Temp_pint, p_levels)
        variable_diff = np.diff(specific_humidity, axis=0) / np.diff(p_levels, axis=0)
        variable_diff[np.isnan(variable_diff)] = -9999
        diff_extreme_idx = np.nanargmax(variable_diff[int(num_plevels/10):-int(num_plevels/8)], axis=0)+int(num_plevels/10)
    elif crit_variable == 'potential_temperature':
        potential_temperature = calc_pot_temp(Temp_pint, p_levels)
        variable_diff = np.diff(potential_temperature, axis=0) / np.diff(p_levels, axis=0)
        variable_diff[np.isnan(variable_diff)] = 9999
        diff_extreme_idx = np.nanargmin(variable_diff[int(num_plevels/10):-int(num_plevels/4)], axis=0)+int(num_plevels/10)
    elif crit_variable == 'pseudopotential_temperature':
        pseudopotential_temperature = calc_pseudopot_temp(RH_pint, Temp_pint, p_levels)
        variable_diff = np.diff(pseudopotential_temperature, axis=0) / np.diff(p_levels, axis=0)
        variable_diff[np.isnan(variable_diff)] = -9999
        diff_extreme_idx = np.nanargmax(variable_diff[int(num_plevels/10):-int(num_plevels/4)], axis=0)+int(num_plevels/10)
    else:
        print('{} is not a valid option as boundary layer indicator.'.format(crit_variable))

    p_mid_levels=np.zeros((p_levels.shape[0]-1, p_levels.shape[1]))
    for p in range(0, p_levels.shape[0]-1):
        p_mid_levels[p] = (p_levels[p+1]+p_levels[p]) / 2
      
    # boundary layer height in pressure coordinates
    p_BL = np.zeros(diff_extreme_idx.shape)
    z_BL = np.zeros(diff_extreme_idx.shape)
    for t in range(len_timeseries):
        arg = diff_extreme_idx[t]
        p_BL[t] = p_mid_levels[arg, t]
    # boundary layer height in altitude coordinates 
    z_mid_levels = np.zeros(variable_diff.shape)
    for t in range(len_timeseries):
        z_levels[:, t] = altitude(p_levels[:, t], Temp_pint[:, t], z0=7)
    # flip altitude array to have the same orientation as p_levels and Temp_pint
    #z_levels = z_levels[::-1]
    
    for lev in range(z_levels.shape[0]-1):
        z_mid_levels[lev] = (z_levels[lev] + z_levels[lev+1]) / 2
    
    z_BL = np.zeros(p_BL.shape)
    for t in range(len_timeseries):
        arg = diff_extreme_idx[t]
        z_BL[t] = z_mid_levels[arg, t]
    
    return z_BL, p_BL
    

def boundary_layer_height_from_ri(Ri, altitudes, threshold=0.2):
    """ Calculates boundary layer height from Bulk Richardson number.
    
    Parameters:
        Ri (array): Bulk Richardson Number
        altitudes (array): altitude levels
        threshold (numeric): Bulk Richardson number associated with the top of
            the boundary layer. Default is 0.2.
    """
    z_BL = np.zeros((Ri.shape[1]))
    for i in range(Ri.shape[1]):
        z_BL[i] = interp1d(Ri[:,i], altitudes[:,i], bounds_error=False, fill_value=np.nan)(0.2)
    
    return z_BL

        
        
###############################################################################

def data_interpolation_z_t(data,ref,z_intv_no,instrument_spef):
    """ file is the filename joined with path.
        instrument_spef is 0 for Alpacas.
        p_intv_no is the number of desired z_levels for Arduinos
    """
    c_p=1005 #J/(kg*K)
    R_l=287  #J/(kg*K)
    
    if instrument_spef == 0:
        #data=np.load(file)
        keys=list(data)
        arduino={}
        unit_time=data[keys[ref]][1:,0]
        key_idx= np.asarray(keys)        #ard_number=np.array([1,2,3,4,5,6,7,8,9,10,11])
        interp_data=np.zeros([len(key_idx),5,len(unit_time)]) # 0 Time, 1 Temp, 2 RH, 3 Pressure, 4 Altitude
        
        for i in range(0,len(keys)):
            for j in range(0,4): # 0 Time, 1 Temp, 2 RH, 3 Pressure
                arduino[keys[i]]=np.asarray(data[keys[i]])
                interp_data[i,j,:]= interp1d(arduino[keys[i]][1::,0],arduino[keys[i]][1::,j],axis=0,fill_value='extrapolate')(unit_time)
        print("Data time interpolated")
        
        for t in range(0,len(unit_time)):
            interp_data[:,4,t] = altitude(interp_data[:,3,t],interp_data[:,1,t],7)
            
        p_min=interp_data[:,3,:].min()
        p_max=interp_data[:,3,:].max()
        p_levels=np.linspace(p_min,p_max,z_intv_no)
        p_levels = np.flip(p_levels,0)
        
        #z_min=interp_data[:,4,:].min()
        z_min = 7
        z_max=interp_data[:,4,:].max()
        z_levels=np.linspace(z_min,z_max,z_intv_no)
        z_interp=np.zeros([len(z_levels),4,len(unit_time)])

            
        for t in range(0,len(unit_time)):
            for j in range(0,4):
                    z_interp[:,j,t]=interp1d(interp_data[::,4,t],interp_data[::,j,t],axis=0,fill_value=np.nan,bounds_error=False)(z_levels)
        print("Data z-interpolated")
    
        Temp_zint=z_interp[:,1,:]
        RH_zint=z_interp[:,2,:]
        p_zint = z_interp[:, 3, :]
        #Pot. Temperatur
        Theta = np.empty((z_intv_no,len(unit_time),))
        Theta.fill(np.nan)
        for t in range(0,len(unit_time)):
            for z in range(0,len(p_levels)):
                Theta[z,t]=(Temp_zint[z,t]+273.15)*(1000/p_levels[z])**(R_l/c_p)        
        return unit_time,z_levels,Temp_zint,RH_zint,Theta, p_zint;
    elif instrument_spef ==1:
        print("Processing of LIDAR data")
        if np.size(z_intv_no) > 1: 
            z_levels= z_intv_no
        else:
            print('Error: if you want interpolate LIDAR/Radiosonde data, you need to insert the p_levels (from Arduino) for the argument p_intv_no')
            sys.exit()
        return None
        
    elif instrument_spef ==2:
        print('Processing of Radiosonde data')
        if np.size(z_intv_no) > 1: 
            z_levels= z_intv_no
        else:
            print('Error: if you want interpolate LIDAR/Radiosonde data, you need to insert the p_levels (from Arduino) for the argument p_intv_no')
            sys.exit()
        return None


###############################################################################        
def smooth_variable(variable, num_timesteps):
    """ Smooths a data field 
    """

    N = num_timesteps
    filt = np.ones((N,))/N
    
    if variable.ndim == 1:
        variable_smoothed = np.zeros(variable.shape[0] - N + 1)
        numlevels = 1
        variable_smoothed = np.convolve(variable, filt, mode='valid')
    else:
        variable_smoothed = np.zeros((variable.shape[0], variable.shape[1] - N + 1))
        numlevels = variable.shape[0]
        for lev in range(numlevels):
            variable_smoothed[lev] = np.convolve(variable[lev], filt, mode='valid')

    return variable_smoothed    


###############################################################################
####### Function reads lidar data and returns list with arrays ################
###############################################################################
    
def read_lidar(path_to_file):
    """
    returns list with arrays containing time [t], height[t,h] level[t,h], windspeed[t,h], winddirection[t,h]
    The file contains 31 variables + 1x metadata in 32 lines/timestep
    Output time is convertet from UTC to CEST (+2 hours)
    Height is calculated by the function (forumula below)
    Variables (note that every variable has len=3):
        'H  ': height = H*18 m-9 m
        'D  ': winddirection [degrees]
        'V  ': windspeed [m/s]
        'VVV': y wind [m/s]
        'VVU': x wind [m/s]
        'VVW': w wind [m/s]]
        'R  ': backscatter [?]  
    FUNCTION NEEDS TO BE MODIFIED TO RETURN META DATA AND RAW DATA BY
    ADDING lidar_data and meta_data to return
    """
    # open file
    data = open(path_to_file,'r').readlines()
    
    # first line is metadata - extract metadata for every timestep
    meta_data = data[::32]
    lidar_data={}
    length=len(data[::32])
    
    # initiate windvectors
    windspeed = np.zeros([length, 90])
    winddirection = np.zeros([length, 90])
    height = np.zeros([length, 90])
    vertical_windspeed = np.zeros([length,90])
    
    # prepare data for extraction
    #the three first characters of every line contain the variable name and thus need to 
    #be stored as dict variables and removed for further processing
    for i in range(1,32):
        lidar_data[data[i][0:3]]=data[i::32][:]
        for j in range(0,len(lidar_data[data[i][0:3]])):
            lidar_data[data[i][0:3]][j]=lidar_data[data[i][0:3]][j][3:]
    
    #extract windinformation. every value has len=6
    for i in range(0,len(lidar_data['H  '])):
        for j in range(0,90):
            try:
                windspeed[i,j] = float(str(lidar_data['V  '][i])[j*6:j*6+6])
            except:
                windspeed[i,j] = np.nan
            try:
                winddirection[i,j] = float(str(lidar_data['D  '][i])[j*6:j*6+6])
            except:
                 winddirection[i,j] = np.nan
            try:
                height[i,j] = float(str(lidar_data['H  '][i])[j*6:j*6+6])
            except:
                 height[i,j] = np.nan
            try:
                vertical_windspeed[i,j] = float(str(lidar_data['VVW'][i])[j*6:j*6+6])
            except:
                 vertical_windspeed[i,j] = np.nan
        
    # calculate hight
    height = height * 18 -9
    
    #time extraction + correction. time is converted from datetime_obj to float 
    #with matplotlib.dates.date2num
    time=np.zeros(len(meta_data))
    for i in range(0,len(meta_data)):
        time[i] = np.int(meta_data[i][4:16])
        time[i] = date2num(datetime.datetime(int('20'+str(time[i])[0:2]),int(str(time[i])[2:4]),
            int(str(time[i])[4:6]),int(str(time[i])[6:8]),int(str(time[i])[8:10]),
            int(str(time[i])[10:12])) + datetime.timedelta(hours=2))
        
    data = [time,height,winddirection,windspeed,vertical_windspeed]
    
    return data

def read_lidar_pkl(path_to_file):
    """ Reads lidar data from .pkl file. Returns list with arrays: 
        lidar_data[0]: time
        lidar_data[1]: altitude
        lidar_data[2]: winddirection
        lidar_data[3]: horizontal windspeed
        lidar_data[4]: vertical windspeed
    """
    with open(path_to_file, 'rb') as f:
        lidar_data = pickle.load(f)
    
    return lidar_data
        
def interpolate_lidar_data(lidar_data,interpolated_arddata_time,interpolated_arddata_z):
    """
    This function interpolates winddata from the lidar on the levels of the Alpacas.
    The Alpacadata is interpolated on the timesteps of the lidar data
    """
    lid_time=lidar_data[0]
    ard_time=interpolated_arddata_time    
    lid_height=lidar_data[1][0,:]
    ard_height=interpolated_arddata_z
    time_interpolated_lid_winddir = interp1d(lid_time,np.transpose(lidar_data[2]), bounds_error=False, fill_value=np.nan)(ard_time)
    time_interpolated_lid_windspeed = interp1d(lid_time,np.transpose(lidar_data[3]), bounds_error=False, fill_value=np.nan)(ard_time)
    time_interpolated_lid_vert_windspeed = interp1d(lid_time,np.transpose(lidar_data[4]), bounds_error=False, fill_value=np.nan)(ard_time)

    interpolated_lid_winddir = np.zeros((ard_height.shape[0], len(ard_time)))  
    interpolated_lid_windspeed = np.zeros((ard_height.shape[0], len(ard_time)))  
    interpolated_lid_vert_windspeed = np.zeros((ard_height.shape[0], len(ard_time)))
    
    for i in range(ard_height.shape[1]):
#        print(lid_height)
#        print(ard_height[:, i])
#        print(np.transpose(time_interpolated_lid_winddir)[i])
        interpolated_lid_winddir[:, i] = interp1d(lid_height, np.transpose(time_interpolated_lid_winddir)[i], bounds_error=False, fill_value=np.nan)(ard_height[:, i])
        interpolated_lid_windspeed[:, i] = interp1d(lid_height, np.transpose(time_interpolated_lid_windspeed)[i], bounds_error=False, fill_value=np.nan)(ard_height[:, i])
        interpolated_lid_vert_windspeed[:, i] = interp1d(lid_height, np.transpose(time_interpolated_lid_vert_windspeed)[i], bounds_error=False, fill_value=np.nan)(ard_height[:, i])
    
    #interpd1(lid_height,)(ard_height)

    return interpolated_lid_winddir, interpolated_lid_windspeed, interpolated_lid_vert_windspeed

def time_averages(variable, variable_time, timestep_boundaries):
    """ A time series of a variable is averaged between timestep_boundaries.
    
    Parameters:
        variable (array): data array (dimensions: altitude/pressure, time)
        variable_time (array): corresponding time array to variable as matplotlib date
        timestep_boundaries (array): Boundaries for new timesteps as matplotlib_date
    """
    
    averaged_variable = np.zeros((variable.shape[0], len(timestep_boundaries)-1))
    for t in range(len(timestep_boundaries)-1):
        averaged_variable[:, t] = np.nanmean(variable[:, np.logical_and(variable_time >= timestep_boundaries[t], 
                                       variable_time < timestep_boundaries[t+1])], axis=1)
    
    return averaged_variable

def get_ceilo_peilo(ceilofeilo):
    """ Takes a path to a CEILOFEILO, returns 
        1. Ceilo time
        2. Ceilo BL height A
    """
    ceilo = np.genfromtxt(ceilofeilo,skip_header = 7,delimiter=';')
    BLA = ceilo[:,-20]
    
    def perdelta(start, end, delta):
        curr = start
        while curr < end:
            yield curr
            curr += delta
            
    f = open(ceilofeilo,'rb')
    for i in range(8):
        KAKA = f.readline()
    ceilo_start = datetime.datetime(int(KAKA[6:10]),int(KAKA[4:5]),int(KAKA[1:2]),1)
    ceilo_end = datetime.datetime(int(KAKA[6:10]),int(KAKA[4:5]),int(KAKA[1:2])+1,0,59)
    
    ceiloteimo = np.zeros(len(BLA))
    for i,result in enumerate(perdelta(ceilo_start, ceilo_end, datetime.timedelta(minutes=1))):
        ceiloteimo[i] = date2num(result)
    ceiloteimo[-1] = date2num(ceilo_end)

    return ceiloteimo, BLA