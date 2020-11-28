import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage.filters import laplace
from scipy.integrate import quad

def fwdEulerStep(x,v,dt):
    x = x + v*dt
    return x

oven = 325
res = 20 # pixels/inch
dV = (0.0254/res)**3 # m^3/pixel
dA = 6*(0.0254/res)**2 # m^2/pixel
t = 45*60 # Total time in sec
steps = 2000
dt = t/steps
pict = 100 # Number of steps between snapshots

# Density of water & flour
# https://www.onlineconversion.com/weight_volume_cooking.htm
d_water = 1.002e3 # kg/m^3
d_flour = 0.507e3 # kg/m^3

# Thermal conductivity
alpha_water = 0.00022165*400 # 0.143e-6 m^2/s with 20 pixels per inch
# https://www.sciencedirect.com/science/article/pii/0260877494000255
alpha_flour = 0.00015810*400 # 0.102e-6 m^2/s

# Heat capacity of water
Cp = 4179.6 # J/kg/K

# Molecular mass of water
# https://www.angelo.edu/faculty/kboudrea/periodic/structure_mass.htm
mm = (2*1.00797 + 15.9994)*1e-3 # kg/mol
R = 8.3144626 # J/K/mol

# Latent heat of vaporization
# https://www.engineeringtoolbox.com/water-properties-d_1573.html
hT = np.array([
    0.01, 2, 4, 10, 14, 18, 20, 25, 30, 34, 40,
    44, 50, 54, 60, 70, 80, 90, 96, 100, 110, 120,
    140, 160, 180, 200, 220, 240, 260, 280, 300,
    320, 340, 360, 373.946]) # deg C
hE = np.array([
    45054, 44970, 44883, 44627, 44456, 44287, 44200,
    43988, 43774, 43602, 43345, 43172, 42911, 42738,
    42475, 42030, 41579, 41120, 40839, 40650, 40167,
    39671, 38630, 37508, 36286, 34944, 33462, 31804,
    29934, 27798, 25304, 22310, 18507, 12967, 0]) # J/mol

# Maxwell-Boltzmann energy distribution
k = 1.38064852e-23 # J/K
def maxwell(E, T):
    Tk = (T-32)*5/9 + 273.15
    return 2*np.sqrt(E/np.pi)*1/(k*Tk)**1.5*np.exp(-E/(k*Tk))

# Evaporation fraction
def evap(T):
    Tc = (T-32)*5/9
    Tk = Tc + 273.15
    Emax = 100*k*Tk
    Evap = np.zeros_like(T)
    frac = np.zeros_like(T)
    Eloss = np.zeros_like(T)
    for i in range(T.shape[0]):
        for j in range(T.shape[1]):
            Evap[i,j] = np.interp(Tc[i,j], hT, hE)/6.02e23
            Eint = np.logspace(np.log10(Evap[i,j]), np.log10(Emax[i,j]), 100)
            frac[i,j] = np.trapz(maxwell(Eint, T[i,j]), Eint)
            Eloss[i,j] = np.trapz(Eint*maxwell(Eint, T[i,j]), Eint)
    return frac, Eloss

n = 40 # 2 in
m = 180 # 9 in
T = 60*np.ones([n,m]) # Starting temp

# Starting water fraction based on
# https://www.thekitchn.com/one-bowl-vanilla-cake-vanilla-sheet-cake-with-sprinkles-244000
mass_flour = 3*d_flour*np.ones([n,m])*dV
mass_water = 2*d_water*np.ones([n,m])*dV
W = (mass_water)/(mass_water+mass_flour)
dW = np.zeros([n,m])

fig, ax = plt.subplots(figsize=(6,4))
for i in range(steps):
    if (i % pict == 0):
        plt.cla()
        plt.matshow(T, fignum=0, cmap=plt.cm.coolwarm, vmin=60, vmax=oven)
        plt.title('Center Temp = '+str(round(T[20,90],1))+
                  ', Minutes = '+str(round(i*dt/60,1)))
        fig.set_size_inches(6,4)
        ax = plt.gca()
        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)
        plt.savefig('temp/wide-'+str(i)+'.png')
        
        plt.cla()
        plt.matshow(W, fignum=0, cmap=plt.cm.Blues, vmin=0.5, vmax=0.6)
        plt.title('Center Hydration = '+str(round(W[20,90],2))+
                  ', Minutes = '+str(round(i*dt/60,1)))
        fig.set_size_inches(6,4)
        ax = plt.gca()
        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)
        plt.savefig('water/wide-'+str(i)+'.png')
        
    frac, Eloss = evap(T)
    mass_water = (np.ones_like(frac)-frac)*mass_water
    dT_evap = Eloss/Cp/mass_water
    T = T - dT_evap
    W = (mass_water)/(mass_water+mass_flour)
    dT = (alpha_water*mass_water + alpha_flour*mass_flour) \
         /(mass_water+mass_flour)*laplace(T,mode='constant',cval=oven)
    T = fwdEulerStep(T,dT,dt)

endT = T[20,90]
print(endT)

n = 40 # 2 in
m = 180 # 9 in
T = 60*np.ones([n,m]) # Starting temp

mass_flour = 3*d_flour*np.ones([n,m])*dV
mass_water = 2*d_water*np.ones([n,m])*dV

fig, ax = plt.subplots(figsize=(6,4))
for i in range(steps):
    if (i % pict == 0):
        plt.cla()
        plt.matshow(T, fignum=0, cmap=plt.cm.coolwarm, vmin=60, vmax=oven)
        plt.title('Center Temp = '+str(round(T[20,90],1))+
                  ', Minutes = '+str(round(i*dt/60,1)))
        fig.set_size_inches(6,4)
        ax = plt.gca()
        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)
        plt.savefig('temp/noevap-'+str(i)+'.png')
        
    dT = (alpha_water*mass_water + alpha_flour*mass_flour) \
         /(mass_water+mass_flour)*laplace(T,mode='constant',cval=oven)
    T = fwdEulerStep(T,dT,dt)

endT = T[20,90]
print(endT)

n = 50 # 2.5 in
m = 160 # 8 in
T = 60*np.ones([n,m])
mass_flour = 3*d_flour*np.ones([n,m])*dV
mass_water = 2*d_water*np.ones([n,m])*dV
W = (mass_water)/(mass_water+mass_flour)
i = 0
while (T[25,80] < endT):
    if (i % pict == 0):
        plt.cla()
        plt.matshow(T, fignum=0, cmap=plt.cm.coolwarm, vmin=60, vmax=oven)
        plt.title('Center Temp = '+str(round(T[25,80],1))+
                  ', Minutes = '+str(round(i*dt/60,1)))
        ax = plt.gca()
        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)
        plt.savefig('temp/narrow-'+str(i)+'.png')
        
        plt.cla()
        plt.matshow(W, fignum=0, cmap=plt.cm.Blues, vmin=0.5, vmax=0.6)
        plt.title('Center Hydration = '+str(round(W[25,80],2))+
                  ', Minutes = '+str(round(i*dt/60,1)))
        ax = plt.gca()
        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)
        plt.savefig('water/narrow-'+str(i)+'.png')
        
    frac, Eloss = evap(T)
    mass_water = (np.ones_like(frac)-frac)*mass_water
    dT_evap = Eloss/Cp/mass_water
    T = T - dT_evap
    W = (mass_water)/(mass_water+mass_flour)
    dT = (alpha_water*mass_water + alpha_flour*mass_flour) \
         /(mass_water+mass_flour)*laplace(T,mode='constant',cval=oven)
    T = fwdEulerStep(T,dT,dt)
    i += 1

print(i*dt)
