import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage.filters import laplace

def fwdEulerStep(x,v,dt):
    x = x + v*dt
    return x

ppc = 20 # pixels/cm
s = 2.0 # cm side length
n = int(s * ppc) # 2 cm cube
# Temperatures of boundary materials
oil = 150
water = 100
air = 20
pict = 100 # Number of steps between snapshots
# https://www.sciencedirect.com/science/article/abs/pii/0260877494000255
alpha = 1.37e-7 # m^2/s thermal diffusivity
# https://wwwf.imperial.ac.uk/blog/physics-of-cooking/2011/03/09/potato-density-changes-with-age-karim-bahsoon/
rho = 1.0923 # g/ml
# https://www.jstage.jst.go.jp/article/nogeikagaku1924/44/12/44_12_587/_article
cp = 2.07108 # J/(g*K)
mass = s**3 * rho # g
dt = min(2/(alpha*(100.0*ppc)**2), 2)
steps = 2000
t = steps*dt # Total time in sec

# Boiling
T = air*np.ones([n,n]) # Starting temp
for i in range(steps):
    if (i % pict == 0):
        plt.matshow(T, vmin=20, vmax=150)
        plt.title('Center Temp = '+str(round(T[int(n/2),int(n/2)],1))+
                  ', Minutes = '+str(round(i*t/steps/60,1)))
        fig = plt.gcf()
        fig.set_size_inches(4,4)
        ax = plt.gca()
        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)
        plt.savefig('water-'+str(i)+'.png')
    dT = alpha*dt*(100.0*ppc)**2*laplace(T,mode='constant',cval=water)
    T = fwdEulerStep(T,dT,t/steps)

endT = T[int(n/2),int(n/2)]
print(endT)

# Frying
T = air*np.ones([n,n]) # Starting temp
for i in range(steps):
    if (i % pict == 0):
        plt.matshow(T, vmin=20, vmax=150)
        plt.title('Center Temp = '+str(round(T[int(n/2),int(n/2)],1))+
                  ', Minutes = '+str(round(i*t/steps/60,1)))
        fig = plt.gcf()
        fig.set_size_inches(4,4)
        ax = plt.gca()
        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)
        plt.savefig('oil-'+str(i)+'.png')
    # Layer of oil on bottom, with air on other sides
    dT = alpha*dt*(100.0*ppc)**2*laplace(np.insert(T, n, oil*np.ones((5,n)),axis=0),
                       mode='constant', cval=air)
    dT = dT[0:n, :]
    T = fwdEulerStep(T,dT,t/steps)

endT = T[int(n/2),int(n/2)]
print(endT)

# Microwave
T = air*np.ones([n,n]) # Starting temp
P = 800 # Watt microwave
ruler = np.linspace(0, 2, n)
xi, yi = np.meshgrid(ruler, ruler)
r = np.sqrt((xi-1)**2 + (yi-1)**2)
# Rough model based on figures in
# https://www.researchgate.net/publicatioint(n/2)27322739_Modeling_and_Simulation_of_Microwave_Heating_of_Foods_Under_Different_Process_Schedules
dMW = (P/4)*np.cos(2*np.pi*r) + P/2
for i in range(steps):
    if (i % pict == 0):
        plt.matshow(T, vmin=20, vmax=150)
        plt.title('Center Temp = '+str(round(T[int(n/2),int(n/2)],1))+
                  ', Minutes = '+str(round(i*t/steps/60,1)))
        fig = plt.gcf()
        fig.set_size_inches(4,4)
        ax = plt.gca()
        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)
        plt.savefig('micro-'+str(i)+'.png')
    dT = alpha*(0.01*ppc)**2*laplace(T, mode='constant', cval=air) + dMW/(cp*mass)*dt
    T = fwdEulerStep(T,dT,t/steps)

endT = T[int(n/2),int(n/2)]
print(endT)
