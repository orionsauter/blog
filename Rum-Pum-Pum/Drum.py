import numpy as np
import matplotlib.pyplot as plt

nt = 1000
nx = 100
R = 10
c = 0.1
drum = round(nx/10)
rho = np.zeros((nt, nx))
rho[0, round(nx/2)] = 0.1 * R
rho[1, round(nx/2)] = 0.075 * R

for t in range(2, nt):
    for x in range(nx):
        rho[t, x] = \
               c*c*rho[t-1, (x-1) % nx] + \
               2 * (1 - c*c) * rho[t-1, x] + \
               c*c*rho[t-1, (x+1) % nx] - \
               rho[t-2, x]
    rho[t, drum] = 0
    rho[t, nx-drum] = 0
    if t % 10 == 0:
        plt.clf()
        plt.plot((R+rho[t, :])*np.sin(np.linspace(0,2*np.pi,nx)),
                 (R+rho[t, :])*-np.cos(np.linspace(0,2*np.pi,nx)),
                 '.-')
        plt.xlim(-1.1*R, 1.1*R)
        plt.ylim(-1.1*R, 1.1*R)
        plt.axes().set_aspect('equal', 'box')
        plt.savefig('ball-'+str(t)+'.png')
