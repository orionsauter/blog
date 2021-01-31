import numpy as np
import matplotlib.pyplot as plt
import control.matlab as ctl

g = 9.8 # m/s^2
L = 1.0 # m
m = 0.1 # kg
w = 0.3
h = 0.2

def plot_pend(ax, x, th, ltype='-'):
    ax.plot([-2,2],[0,0],'-k')
    ax.plot([x-w/2,x+w/2,x+w/2,x-w/2,x-w/2],
            [0,0,h,h,0], ltype+'b')
    ax.plot([x,x-L*np.sin(th)],[h,h+L*np.cos(th)],ltype+'r')
    ax.axis("equal")
    ax.set_xlim((-2,2))
    ax.set_ylim((-0.1,h+L+0.1))

def ang_acc(th, thd, F):
    thdd = (3*(-F*np.cos(th) - g*m*np.sin(th) +
               L*m*thd**2*np.cos(th)*np.sin(th)))\
               /(L*m*(-4 + 3*np.cos(th)**2))
    return thdd

def lin_acc(th, thd, F):
    xdd = -((1/np.cos(th)*(4*F*np.cos(th) - 4*L*m*thd**2*np.cos(th)*np.sin(th)
                         + 3*g*m*np.cos(th)**2*np.sin(th)))
            /(m*(-4 + 3*np.cos(th)**2)))
    return xdd

A = np.array([[0, 0, 1, 0],
              [0, 0, 0, 1],
              [0, 3*g, 0, 0],
              [0, 3*g/L, 0, 0]])
B = np.array([[0, 0, 4/m, 3/(m*L)]])
C = np.array([[1, 0, 0, 0],
              [0, 1, 0, 0]])
D = np.array([[0], [0]])
dt = 0.05
##pend = ctl.ss(A, B, C, D, dt)
##fb = ctl.ss(0,np.zeros((1,2)),0,np.array([[0, m*g]]),dt)
##simt = np.arange(0,1,dt)
##yout, t, _ = ctl.lsim(
##    ctl.feedback(pend,fb),
##    U=np.zeros((1,len(simt))),
##    T=simt,
##    X0=np.array([0,0.2,0,0]))
##print(yout)
t = np.arange(0,3,dt)
x = np.zeros((len(t),4))
x_lin = np.zeros((len(t),4))
x[0,:] = np.array([0,0.2,0,0])
x_lin[0,:] = np.array([0,0.2,0,0])
F = 0
fig, ax = plt.subplots(figsize=(4,4))
for i in range(len(t)-1):
    xdd = lin_acc(x[i,1], x[i,3], F)
    thdd = ang_acc(x[i,1], x[i,3], F)
    xdd_lin = A@x[i,:].T + B*F
    x_lin[i+1,:] = x_lin[i,:] + xdd_lin*dt
    x[i+1,:2] = x[i,:2] + x[i,2:]*dt
    x[i+1,2] = x[i,2] + xdd*dt
    x[i+1,3] = x[i,3] + thdd*dt
    ax.clear()
    plot_pend(ax, x[i,0], x[i,1], ltype='-')
    plot_pend(ax, x_lin[i,0], x_lin[i,1], ltype=':')
    plt.savefig("frames/unforced-{}.png".format(i))
for i in range(len(t)-1):
    F = -1.7*m*g*(x[i,1] + 0.6*x[i,3]*dt)
    xdd = lin_acc(x[i,1], x[i,3], F)
    thdd = ang_acc(x[i,1], x[i,3], F)
    xdd_lin = A@x[i,:].T + B*F
    x_lin[i+1,:] = x_lin[i,:] + xdd_lin*dt
    x[i+1,:2] = x[i,:2] + x[i,2:]*dt
    x[i+1,2] = x[i,2] + xdd*dt
    x[i+1,3] = x[i,3] + thdd*dt
    ax.clear()
    plot_pend(ax, x[i,0], x[i,1], ltype='-')
    plot_pend(ax, x_lin[i,0], x_lin[i,1], ltype=':')
    plt.savefig("frames/forced-{}.png".format(i))

