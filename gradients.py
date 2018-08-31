# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 14:18:27 2018

@author: Henning
"""
def gradient_profile_plot_series(filename,server_path,unit_time,Temp_diff,Theta_diff,RH_diff,p_mid_levels):
    ###########################################################################
    ##Plot data
    fig_name="Gradients"+filename[:-4]+".png"
    fig_title="Date "+filename[6:8]+"."+filename[4:6]+"."+filename[0:4]+" ,Start Time: "+filename[8:10]+":"+filename[10:12]+":"+filename[12:14] 
    ###########################################################################
    print("Plotting...")
    fig= plt.figure(figsize=(15,10))
    matplotlib.rcParams.update({'font.size': 14})
    
    #levels_T=np.arange(12,23,0.5)
    #levels_Theta=np.arange(14,25,0.5)
    ###########################################################################
    #Subplot1: Temperatur
    #ax1=fig.add_subplot(311)
    #X,Y = np.meshgrid(unit_time,p_levels)
    #C= ax1.contourf(X,Y,Temp_pint,levels_T,cmap=plt.get_cmap("hot_r", len(levels_T)-1),extend="both")
    #cb=plt.colorbar(C)
    #cb.set_label('Temperatur in $^\circ$C',fontsize=16)
    #
    #ax1.set_xticks(ax1.get_xticks()[::])
    #ax1.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
    #ax1.set_xlim([unit_time[0],unit_time[-1]])
    #ax1.set_xlabel('Local Time')
    #ax1.set_ylabel('Pressure in hPa')
    #ax1.grid()
    #Plot Title
    #fig_title="Date "+filename[6:8]+"."+filename[4:6]+"."+filename[0:4]+" ,Start Time: "+filename[8:10]+":"+filename[10:12]+":"+filename[12:14] 
    #plt.title(fig_title, fontsize=16)
    #extra settings for axes and ticks
    #plt.setp(plt.gca().xaxis.get_majorticklabels(),'rotation', 30)
    #plt.gca().invert_yaxis()
    #plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
    #            wspace=None, hspace=0.3)# for space between the subplots  
    ###################################### 
    #Subplot2 pot. Temperatur
    ax2=fig.add_subplot(211)
    X,Y = np.meshgrid(unit_time,p_mid_levels)
    levels_Theta=np.arange(-0.6,0.7,0.1)
    C2= ax2.contourf(X,Y,Theta_diff,levels_Theta,cmap=plt.get_cmap("coolwarm",len(levels_Theta)-1),extend="both")
    cb=plt.colorbar(C2)
    cb.set_label('$\delta \Theta / \delta$p\n in K/hPa',fontsize=16)
    cb.set_ticks(levels_Theta)
    ax2.set_xticks(ax2.get_xticks()[::])
    ax2.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
    ax2.set_xlim([unit_time[0],unit_time[-1]])
    ax2.grid()
    #ax2.set_xlabel('Local Time')
    ax2.set_ylabel('Pressure in hPa')
    ax2.set_ylim([p_mid_levels[0],p_mid_levels[-1]])
    plt.gca().invert_yaxis()
    plt.setp(plt.gca().xaxis.get_majorticklabels(),'rotation', 30)
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                wspace=None, hspace=0.3)   
    ######################################
    #Subplot3 Relative Humidity
    ax3=fig.add_subplot(212)
    C3= ax3.contourf(X,Y,RH_diff,cmap=plt.get_cmap("viridis_r"))
    cb=plt.colorbar(C3)
    cb.set_label('$\delta RH / \delta p $ in %/hPa',fontsize=16)
    ax3.set_xticks(ax3.get_xticks()[::])
    ax3.xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
    ax3.set_xlim([unit_time[0],unit_time[-1]])
    #ax3.set_xlabel('Local Time')
    ax3.set_ylabel('Pressure in hPa')
    ax3.grid()
    ax3.set_ylim([p_mid_levels[0],p_mid_levels[-1]])
    plt.gca().invert_yaxis()
    plt.setp(plt.gca().xaxis.get_majorticklabels(),'rotation', 30)
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                wspace=None, hspace=0.3)
    fig.savefig(fig_name, dpi=500,bbox_inches='tight')
    fig.savefig(server_path+fig_name,dpi=500,bbox_inches="tight")
    plt.close()
    print("Plotted Gradients and stored them on server")
    return        

