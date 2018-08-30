
import sys
import numpy as np
from scipy.interpolate import interp1d
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
###############################################################################
def apply_correction(data):
    """ Applies temperature and humidity correction to ALPACA raw data and 
    returns a dictionary with the same structure as in the raw data, but 
    with the corrected values. 
    """
    
    
    arduinos = data.keys()
    
    temp_correction = {1: 0.09, 2: 0.10, 3: -0.02, 4: -0.23, 5: -0.20,
                       6: 0.05, 7: 0.15, 8: 0.12, 9: -0.10, 10: 0.11,
                       11: -0.08}
    
    humidity_correction = {1: -0.15, 2: 0.28, 3: -0.09, 4: 0.08, 5: 0.41,
                       6: -0.19, 7: -2.16, 8: 1.01, 9: -0.64, 10: -0.35,
                       11: 2.01}
    
    for i in arduinos:
        # temperature
        data[i][1:, 1] = data[i][1:, 1] + temp_correction[i]
        # humidity
        data[i][1:, 2] = data[i][1:, 2] + humidity_correction[i]
    print("Data calibrated")    
    return data
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
        return unit_time,p_levels,Temp_pint,RH_pint,Theta;
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
def altitude(pressure, temperature):
    """ Calculates altitude fromm pressure and temperature.
    
    Parameters:
        pressure (array): vertical pressure profile 
        temperature (array): vertical temperature profile
    """
    
    # constants
    R = 287.058
    g = 9.81
    z = np.zeros(len(pressure))
    z_interv = np.zeros(len(pressure))
    z0 = 7.0

    for lev in range(0, len(pressure)-1):
        z_interv[lev+1] = np.log(pressure[lev+1] / pressure[lev]) * -(R * (temperature[lev] + temperature[lev+1]) / 2 / g)
        
        z[lev+1] = np.sum(z_interv)
        
    return z + z0

