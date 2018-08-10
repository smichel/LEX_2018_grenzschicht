import serial
import time
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import date2num
from matplotlib import dates
from datetime import datetime

jet = plt.get_cmap('gist_rainbow',10)

#data = np.load('C:/Users/Uni/LEX_2018_grenzschicht/20180806170236.npy')
#data = np.load('C:/Users/Uni/LEX_2018_grenzschicht/20180806112200.npy')
data = np.load('C:/Users/Uni/LEX_2018_grenzschicht/20180807121203.npy') #büro regal
#data = np.load('C:/Users/Uni/LEX_2018_grenzschicht/20180806200646.npy') # simon keller
kellerpeter = 22.72
#('C:/Users/Uni/AppData/Local/VirtualStore/Program Files/Measure/P755_20180806_4.dbf')
#peter=np.genfromtxt('C:/Users/Uni/LEX_2018_grenzschicht/P755_20180806_2.txt')
peter=np.genfromtxt('C:/Users/Uni/AppData/Local/VirtualStore/Program Files/Measure/P755_20180806_4.dbf')

peter=peter[~np.isnan(peter)]
peter=peter[0:-1]
peter=np.reshape(peter,(int(len((peter))/2),2))
peter[(peter[:,1]<10 )| (peter[:,1]>30),1] = np.nan

#starttime = dates.date2num(datetime.strptime('20180804231851', '%Y%m%d%H%M%S')) # balkon
#endtime = dates.date2num(datetime.strptime('20180805114806', '%Y%m%d%H%M%S'))  # balkon
starttime = dates.date2num(datetime.strptime('20180806200639', '%Y%m%d%H%M%S'))
endtime =   dates.date2num(datetime.strptime('20180807100002', '%Y%m%d%H%M%S'))
petertime=np.linspace(starttime,endtime,len(peter))
arduino=10*['']
temps=10*['']
for i in range(1,11):
    arduino[i-1]=np.asarray(data[i])
    arduino[i-1][(arduino[i-1][:, 1] < 20) | (arduino[i-1][:, 1] > 35), 1]=np.nan
    arduino[i-1][(arduino[i-1][:, 2] < 20) | (arduino[i-1][:, 2] > 100), 2]=np.nan
    arduino[i-1][(arduino[i-1][:, 3] < 970) | (arduino[i-1][:, 3] > 1030), 3]=np.nan
    temps[i-1]=arduino[i-1][:,1]

for i in range(10):
    for j in range(1,len(arduino[i])):
        if arduino[i][j,4]<arduino[i][j-1,4]:
            arduino[i][j,4]=arduino[i][j-1,4]+1

plt.figure()
plt.plot(arduino[0][:, 4])
plt.show(block=False)


Tmedians=np.zeros(10)
for i in range(10):
    Tmedians[i]=np.nanpercentile(temps[i],50)


for j in range(1,4):
    plt.figure()
    for i in range(10):
        arduino[i-1][0, 4]=np.nan

        plt.plot(arduino[i][:,4],arduino[i][:,j],color=jet(i),label=str(i))

    plt.legend()

plt.show(block=False)
tcorr=kellerpeter-Tmedians
plt.figure()
for i in range(10):
    plt.plot(arduino[i][:, 4], arduino[i][:, 1],color=jet(i))
    plt.plot(arduino[i][:, 4], [Tmedians[i]]*len(arduino[i][:, 4]), color=jet(i), Linestyle='--')

plt.show(block=False)
Tcorr=[0.005, 0.16, 0.14, -0.02, -0.22, 0.28, 0.42, 0.41, -0.21, -2.842170943040401e-14]

plt.figure()
for i in range(10):
    plt.plot(arduino[i][:, 4], arduino[i][:, 1]+Tcorr[i],color=jet(i))


plt.plot(arduino[0][:, 4], [kellerpeter] * len(arduino[0][:, 4]), color='k')
plt.show(block=False)

plt.figure()

for i in range(10):
    plt.plot(arduino[i][:, 0], arduino[i][:, 1],color=jet(i),label=str(i))

plt.plot(petertime, peter[:,1],color='k')
plt.legend()
plt.show(block=False)

startidxpeter=np.min(np.where(petertime>(7.3691e5+2.97)))
endidxpeter=np.min(np.where(petertime>(7.3691e5+3.11)))
startidxardu=np.zeros(10)
endidxardu=np.zeros(10)
ardumean=np.zeros(10)
arducorr=np.zeros(10)
feuchtgebiete=np.zeros(10)
ardupetercorr = np.zeros(10)
petermean=np.nanmean(peter[startidxpeter:endidxpeter,1])
for i in range(10):
    startidxardu[i] = np.min(np.where(arduino[i][:,0] > (7.3691e5+2.97)))
    endidxardu[i] = np.min(np.where(arduino[i][:,0] > (7.3691e5+3.11)))
    ardumean[i]=np.nanmean(arduino[i][int(startidxardu[i]):int(endidxardu[i]),1])
    feuchtgebiete[i] = np.nanmean(arduino[i][int(startidxardu[i]):int(endidxardu[i]),2])


totalardumean = np.nanmean(ardumean)
totalefeuchte = np.nanmean(feuchtgebiete)

arducorr = totalardumean - ardumean
ardupetercorr = petermean-ardumean
feuchtcorr = totalefeuchte - feuchtgebiete

plt.figure()


#Arducorr=[-0.07900497296344966, -0.49866936005048856, -1.5650055264766038, -0.7172463550255692, -0.6075512744163767, 0.19128818216834986, -0.43866752775674556, 0.16499228385954723, -0.28690686171278657, 0.18096030536596786]
finalefeuchtcorr = [2.6967455282278791, 2.019810301232212, 0.7988041850625507, 0.33789509780086746, 1.4866460360382234, -1.4921282077773412, -2.214225778675157, 0.7299801435411979, -3.2266263048570636, -0.31907172948442053]
finaletempcorr= [-0.20298338235838642, -0.03457388306773623, -0.14143909679448186, -0.21896698336938059, -0.31915655917819663, 0.27426237148132415, 0.17265320130558948, 0.1972397629378655, 0.14218800363267192, 0.13077656541075555]
petertempcorr = [-0.97744274, -0.80903324, -0.91589846, -0.99342634, -1.09361592, -0.50019699, -0.60180616, -0.5772196,  -0.63227136, -0.64368279]
for i in range(10):
    plt.plot(arduino[i][:, 0], arduino[i][:, 1]+ardupetercorr[i],color=jet(i),label=str(i))

plt.plot(petertime, peter[:,1],color='k')
plt.legend()
plt.show(block=False)

plt.figure()

for i in range(10):
    plt.plot(arduino[i][:, 0], arduino[i][:, 2]+feuchtcorr[i],color=jet(i),label=str(i))

plt.legend()
plt.show(block=False)
print(1)