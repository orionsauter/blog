import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import animation
plt.rcParams['animation.ffmpeg_path'] = '/usr/local/bin/ffmpeg'

# Set up formatting for the movie files
Writer = animation.writers['ffmpeg']
writer = Writer(fps=100, metadata=dict(artist='Me'), bitrate=1800)

N = 15 # Number of segments
L = 10 # Total length (cm)
m = 10 # Total mass (g)
dt = 0.01 # Time step (s)
th0 = 2*np.pi/5 # Angle of ears
k = 200 # Stiffness of ears
g = 980 # Acceleration from gravity (cm/s^2)
mu = 5 # Damping
freq = 15 # Stride frequency (Hz)
amp = 15 # Stride amplitude
mdist = 'quad' # Mass distribution
fig, ax = plt.subplots()

for k in (200, 400):
    for mdist in ('unif', 'lin', 'quad'):
        # Setup
        fig.clear()
        th = np.zeros(N)
        th[0] = th0
        dth = np.zeros(N)
        if (mdist == 'unif'):
            dist = np.ones(N)
        elif (mdist == 'lin'):
            dist = np.arange(N+6, 6, -1)
        elif (mdist == 'quad'):
            dist = np.arange(N+10, 10, -1)**2
        dm = m*dist/np.sum(dist)
        dL = L/N
        dI = dm*dL**2/3
        ears, = plt.plot([],[],'-')

        # Transform angles to (x,y)
        def th2xy(th):
            thtot = np.cumsum(th, axis=0)
            dxy = np.zeros((N, 2))
            for i in range(N):
                dxy[i,:] = [dL*np.cos(thtot[i]), dL*np.sin(thtot[i])]
            dxy = np.insert(dxy, 0, [0, 0], axis=0)
            xy = np.cumsum(dxy, axis=0)
            return xy

        # Plot segments
        def draw(th):
            fig.clear()
            xy = th2xy(th)
            ears, = plt.plot(xy[:,0],xy[:,1],'.-')
            plt.xlim([-0.1, 1.0*L])
            plt.ylim([-0.1, 1.0*L])
            return ears

        # Calculate torque
        def torque(frame, th, dth):
            trq = np.zeros(N)
            thtot = np.cumsum(th, axis=0)
            for i in range(N):
                theta = th[i]
                if i == 0:
                    theta -= th0
                trq[i] = -k*theta - dI[i]/4*g*np.cos(thtot[i]) - mu*dth[i]
            trq[0] += amp*np.sin(freq*frame)
            return trq

        # Init function for animation
        def init():
            plt.xlim([-0.1, 1.0*L])
            plt.ylim([-0.1, 1.0*L])
            return ears,

        # Perform integration
        def update(frame, th, dth, ears):
            th += dth*dt
            dth += torque(frame, th, dth)*dt/dI
            xy = th2xy(th)
            ears.set_data(xy[:,0], xy[:,1])
            return ears,

        ani = animation.FuncAnimation(fig, update, frames=np.arange(0, 10, 0.01),
                                      init_func=init, fargs=[th, dth, ears],
                                      blit=True, interval=dt*1e3)
        f = open('ears-'+mdist+'-'+str(k)+'.html', 'w')
        f.write(ani.to_html5_video())
        f.close()
