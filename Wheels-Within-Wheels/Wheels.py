import numpy as np
import matplotlib.pyplot as plt

R = 1 # Container radius
r = 0.1 # Wheel radius
g = 9.8 # Acc of gravity
th0 = -np.pi/6 # Initial angle
x0 = R*np.sin(th0)
y0 = R - R*np.cos(th0)
nsteps = 150
nT = 5 # Number of periods
q = np.array([0, 0.4, 0.5, 1]) # Rot inertia factors
names = ["no frict.", "sphere", "cyl.", "ring"]
colors = ["m", "b", "r", "g"]
w = np.sqrt(g/R/(1 + q))
T = 2*np.pi/w
dt = np.min(T)*nT/nsteps
fig, ax = plt.subplots(figsize=(6,3))
ax.axis('off')
for i in range(nsteps):
    ax.cla()
    ax.axis('off')
    t = dt*i
    ax.set_title("t = {:.2f}".format(t))
    thR = th0 * np.cos(w*t)
    thr = R/r * thR
    ax.add_artist(plt.Circle([0,R], R, color="k", fill=False))
    plt.xlim(-R, R)
    plt.ylim(0, R)
    for j in range(len(names)):
        xy = (R-r)*np.sin(thR[j]), R-(R-r)*np.cos(thR[j])
        ax.add_artist(plt.Circle(xy, r, color=colors[j], fill=False))
        if j > 0:
            plt.plot([xy[0], xy[0] + r*np.sin(thr[j])],
                     [xy[1], xy[1] + r*np.cos(thr[j])],
                     color = colors[j], linestyle = "solid", marker = None,
                     label = names[j])
        else:
            plt.plot([xy[0], xy[0] + r*np.sin(R/r*th0)],
                     [xy[1], xy[1] + r*np.cos(R/r*th0)],
                     color = colors[j], linestyle = "solid", marker = None,
                     label = names[j])
    plt.legend(loc="upper center")
    plt.savefig("frames/wheel-{:03d}.png".format(i))
