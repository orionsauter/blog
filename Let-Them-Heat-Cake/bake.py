import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage.filters import laplace

def fwdEulerStep(x,v,dt):
    x = x + v*dt
    return x

n = 40 # 2 in
m = 180 # 9 in
T = 60*np.ones([n,m]) # Starting temp
oven = 325
t = 45*60 # Total time in sec
steps = 2000
pict = 100 # Number of steps between snapshots
alpha = 0.00022165*400 # 0.143e-6 m^2/s with 20 pixels per inch

for i in range(steps):
    if (i % pict == 0):
        plt.matshow(T)
        plt.title('Center Temp = '+str(round(T[20,90],1))+
                  ', Minutes = '+str(round(i*t/steps/60,1)))
        fig = plt.gcf()
        fig.set_size_inches(6,4)
        ax = plt.gca()
        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)
        plt.savefig('wide-'+str(i)+'.png')
    dT = alpha*laplace(T,mode='constant',cval=oven)
    T = fwdEulerStep(T,dT,t/steps)

endT = T[20,90]
print endT

n = 50 # 2.5 in
m = 160 # 8 in
T = 60*np.ones([n,m])
i = 0
while (T[25,80] < endT):
    if (i % pict == 0):
        plt.matshow(T)
        plt.title('Center Temp = '+str(round(T[25,80],1))+
                  ', Minutes = '+str(round(i*t/steps/60,1)))
        fig = plt.gcf()
        fig.set_size_inches(6,4)
        ax = plt.gca()
        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)
        plt.savefig('narrow-'+str(i)+'.png')
    dT = alpha*laplace(T,mode='constant',cval=oven)
    T = fwdEulerStep(T,dT,t/steps)
    i += 1

print i*t/steps
