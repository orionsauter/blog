import numpy as np
import matplotlib.pyplot as plt

def RotMat(th):
    return np.matrix([[np.cos(th), -np.sin(th)],
                      [np.sin(th), np.cos(th)]])

a = 1./np.sqrt(2) # Distance from pivot to wheel center
b = 0.5 # Radius of wheel
c = a * np.sqrt(3) # Distance between wheels
h = b/a + a # Height of pivot
phi = np.pi/6 # Initial angle of wheels
om = -np.pi/3 # Angular velocity of wheels
R = RotMat(np.pi/4) # 45° rotation matrix
lim = 4
fig, ax = plt.subplots()
plt.axis('scaled')

# Plot circle around point cent
def Wheel(cent):
    return plt.Circle(cent, b, color='b', fill=False)

# Triangle wave to represent stairs (horizontal)
def Stairs(t):
    u = np.arange(-2*(lim-c/2), 2*lim, c/2)
    s = np.zeros((2, len(u)))
    for i in range(len(u)):
        if i % 2 == 0:
            s[:, i] = [u[i] - c*t/2, c/2]
            #s[:, i] = [u[i], c/2]
        else:
            s[:, i] = [u[i] - c*t/2, 0]
            #s[:, i] = [u[i], 0]
    return s

# Put everything together
def Frame(t):
    ax.cla()
    # Get the stairs shifted to t
    s = Stairs(t)
    # Rotate to 45°
    s = np.array(np.dot(R, s))
    plt.plot(s[0, :], s[1, :], '-k')
    # Get rotation matrix for wheels
    T = RotMat(om * t)
    # Wheel centers
    cents = np.array([[a * np.cos(2*np.pi/3 * n + phi),
        a * np.sin(2*np.pi/3 * n + phi) + h - a] for n in range(3)])
    # Rotate to given time
    cents = [np.dot(T, np.transpose([cent])) for cent in cents]
    # Shift to align with stairs
    cents = [cent + np.array([[-c*t/2],[a]]) for cent in cents]
    #cents = [cent + np.array([[0],[a]]) for cent in cents]
    # Rotate to 45°
    cents = [np.dot(R, cent) for cent in cents]
    for cent in cents:
        ax.add_artist(Wheel(cent))

times = np.linspace(-1, 1, 51)
for i in range(len(times)):
    Frame(times[i])
    ax.set_xlim((-lim, lim))
    ax.set_ylim((-lim, lim))
    plt.savefig("steps"+str(i)+".png")
