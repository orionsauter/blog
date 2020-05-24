import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

def gauss(x, sd):
    return np.exp(-0.5*(x/sd)**2)

def deriv(x, y):
    # Use grad to get same size result
    xp = np.gradient(x)
    yp = np.gradient(y)
    return xp, yp

def osc(x, y):
    xp, yp = deriv(x, y)
    xpp, ypp = deriv(xp, yp)
    pmag = np.sqrt(xp*xp + yp*yp)
    R = (xp*xp + yp*yp)**1.5/np.abs(xp*ypp - yp*xpp)
    xc = x - R/pmag * yp
    yc = y + R/pmag * xp
    return xc, yc, R

n = 101
sd = 0.5 # m
A = 0.75 # m
v = 13.4 # m/s = 30 mph
d = 6 # m
g = 9.8 # m/s^2
xinit = np.linspace(-d/2, d/2, n)
yinit = A*gauss(xinit, sd)
xp, yp = deriv(xinit, yinit)
s = np.sum(np.sqrt(xp*xp + yp*yp))
dt = s/v
ds = s/n
ds2 = ds*ds
x = [xinit[0]]
y = [yinit[0]]
# Build up x points to get const speed
while x[-1] < 3:
    adj = 0.1
    dx = ds
    dy = A*gauss(x[-1]+dx, sd) - y[-1]
    test = dx*dx + dy*dy
    while np.abs(test - ds2)/ds2 > 0.1:
        if test > ds2:
            dx = (1-adj)*dx
        else:
            dx = (1+adj)*dx
        dy = A*gauss(x[-1]+dx, sd) - y[-1]
        test = dx*dx + dy*dy
    x += [x[-1] + dx]
    y += [y[-1] + dy]
x = np.array(x)
y = np.array(y)
xc, yc, R = osc(x, y)

# Plot osculating circles
fig, ax = plt.subplots(figsize=(4,3))
for i in range(n):
    ax.clear()
    ax.plot(x, y, '-k')
    ax.plot(x[i], y[i], '.b')
    c = Circle((xc[i], yc[i]), R[i], ec='blue', fill=False)
    ax.add_patch(c)
    plt.axis('equal')
    plt.xlim((-3,3))
    plt.ylim((-0.1,3))
    plt.savefig('frames/osc-{}.png'.format(i), bbox_inches='tight')

# Plot y-accel
xp, yp = deriv(x, y)
xpp, ypp = deriv(xp, yp)
fig, ax = plt.subplots(figsize=(4,3))
plt.plot(x, ypp/dt/dt/g, '-b')
plt.xlabel('x pos (m)')
plt.ylabel('y acc (g)')
plt.savefig('accel.png'.format(i), bbox_inches='tight')
