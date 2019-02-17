import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import animation
plt.rcParams['animation.ffmpeg_path'] = '/usr/local/bin/ffmpeg'

# Set up formatting for the movie files
Writer = animation.writers['ffmpeg']
writer = Writer(fps=100, metadata=dict(artist='Me'), bitrate=1800)

N = 16
L = 10
m = 10
dt = 0.01
th0 = 2*np.pi/5
k = 200
g = 980
mu = 5
freq = 15
amp = 15
fig, ax = plt.subplots()

th = np.zeros((N, 1))
th[0,0] = th0
dth = np.zeros((N, 1))
dm = m/N
dL = L/N
dI = dm*dL**2/3
ears, = plt.plot([],[],'-')

def th2xy(th):
    thtot = np.cumsum(th, axis=0)
    dxy = np.zeros((N, 2))
    for i in range(N):
        dxy[i,:] = [dL*np.cos(thtot[i]), dL*np.sin(thtot[i])]
    dxy = np.insert(dxy, 0, [0, 0], axis=0)
    xy = np.cumsum(dxy, axis=0)
    return xy

def draw(th):
    fig.clear()
    xy = th2xy(th)
    ears, = plt.plot(xy[:,0],xy[:,1],'.-')
    plt.xlim([-0.1, 1.0*L])
    plt.ylim([-0.1, 1.0*L])
    return ears

def init():
    plt.xlim([-0.1, 1.0*L])
    plt.ylim([-0.1, 1.0*L])
    return ears,

def update(frame, th, dth, ears):
    th += dth*dt
    dth += torque(frame, th, dth)*dt/dI
    xy = th2xy(th)
    ears.set_data(xy[:,0], xy[:,1])
    return ears,

def torque(frame, th, dth):
    trq = np.zeros((N, 1))
    thtot = np.cumsum(th, axis=0)
    for i in range(N):
        theta = th[i,0]
        if i == 0:
            theta -= th0
        trq[i,0] = -k*theta - dI/4*g*np.cos(thtot[i,0]) - mu*dth[i,0]
    trq[0,0] += amp*np.sin(freq*frame)
    return trq

ani = animation.FuncAnimation(fig, update, frames=np.arange(0, 10, 0.01),
                              init_func=init, fargs=[th, dth, ears], blit=True)
ani.save('ears.mp4', dpi=100, writer=writer)
