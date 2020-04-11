import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

nstep = 8000
n = 30 # Number of points in arrow
L = 10.0 # Length of arrow
r = 1.0 # Width of bow
s = 1.0e-3 # Damping of vibrations
dt = 0.25
dL = L / n
bowPos = np.array([[0, L]])

def display(t, th, tip):
    fig, ax = plt.subplots(figsize=(4,3))
    bow = mpatches.Circle(bowPos[0,:], r, color='red')
    shaft = np.zeros((n, 2))
    shaft[-1,:] = tip
    for i in range(n-1)[::-1]:
        shaft[i,:] = shaft[i+1,:] - \
                     [-dL*np.cos(th[i]), dL*np.sin(th[i])]
    ax.axis('equal')
    plt.plot(shaft[:,0], shaft[:,1], '-')
    ax.add_patch(bow)
    plt.savefig('frames/arrow-{}.png'.format(t), bbox_inches='tight')
    plt.close(fig)

# Don't let the arrow intersect the bow
def bowNorm(th, tip):
    dr = tip - bowPos
    dist2 = np.sum((dr)**2)
    if (dist2 < r*r):
        dist = np.sqrt(dist2)
        tip += dr * (r-dist)/dist
    pos = tip
    for i in range(n-1)[::-1]:
        newPos = pos - [-dL*np.cos(th[i]), dL*np.sin(th[i])]
        dr = newPos - bowPos
        dist2 = np.sum((dr)**2)
        if (dist2 < r*r):
            dist = np.sqrt(dist2)
            newPos += dr * (r-dist)/dist
            th[i] = np.arctan2((pos[0,1]-newPos[0,1])/dL,
                               (newPos[0,0]-pos[0,0])/dL)
        pos = newPos
    return th, tip

def simulate(tmass, k, plot=True):
    masses = np.ones((n,))
    masses[-1] = tmass
    # Rotational inertia for segments
    I = 0.5 * masses * dL**2
    th = np.arctan2(L, r) * np.ones((n,))
    tip = np.array([[-r, L]])

    force = np.zeros((n, 2))
    veloc = np.zeros((2,))
    omega = np.zeros((n,))
    force[0, 1] = 1.0e-1
    force[0,:] *= 0.9
    if plot:
        display(0, th, tip)

    for t in range(1, nstep+1):
        th += dt * omega
        tip += dt * veloc
        if (np.sum((tip - bowPos)**2) < L*L):
            th, tip = bowNorm(th, tip)
        dth = np.diff(th)
        vec = np.array([[np.cos(ang), np.sin(ang)] for ang in th])
        perp = np.hstack((-vec[:,[1]], vec[:,[0]]))
        tailbend = -k*np.concatenate(([0], dth))
        tipbend = k*np.concatenate((dth, [0]))
        fpara = np.tile(np.sum(force * vec, axis=1).reshape((n,1)), (1,2)) * vec
        fperp = np.sum(force - fpara, axis=1)
        torque = fperp * dL + tailbend + tipbend
        force[0,:] *= 0.5
        force[1:,:] = fpara[:-1,:]
        omega += dt * (torque/I - s * omega)
        veloc += dt * force[-1,:]/masses[-1]
        if t % 50 == 0 and plot:
            display(t, th, tip)
    return tip

karr = np.logspace(np.log10(0.001), np.log10(0.51), 20)
marr = np.linspace(8.828, 8.833, 20)
X, Y = np.meshgrid(marr, karr)
data = np.zeros((len(karr), len(marr)))
for i in range(len(karr)):
    print('{}/{}'.format(i, len(karr)))
    for j in range(len(marr)):
        data[i,j] = simulate(marr[j], karr[i], plot=False)[0,0]

fig, ax = plt.subplots(figsize=(4,3))
plt.pcolormesh(X, Y, np.abs(data), cmap=plt.cm.YlOrRd)
plt.yscale('log')
plt.colorbar()
plt.xlabel('tip mass')
plt.ylabel('k')

ind = np.unravel_index(np.argmin(np.abs(data), axis=None), data.shape)
simulate(marr[ind[1]], karr[ind[0]], plot=True)
