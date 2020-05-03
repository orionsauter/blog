import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as pch

# Arbitrary units, estimated from photo
armJoint = np.array([0.0, 1.8])
footJoint = np.array([0.0, 1.0])
r1 = 0.5
r2 = 1.75
R1 = 1.5
R2 = 1.35

# Using derivation at http://paulbourke.net/geometry/circlesphere/
def calcFootPos(th1, th2):
    wheelPos = footJoint + r1 * np.array([np.cos(th1), np.sin(th1)])
    armPos = armJoint + r2 * np.array([np.sin(th2), -np.cos(th2)])
    dVec = wheelPos - armPos
    d = np.linalg.norm(dVec)
    a = (R1*R1 - R2*R2 + d*d)/(2*d)
    h = np.sqrt(R1*R1 - a*a)
    cent = wheelPos + a*(armPos - wheelPos)/d
    footPos1 = cent + h*np.array([-1,1])*dVec[::-1]/d
    footPos2 = cent - h*np.array([-1,1])*dVec[::-1]/d
    if footPos1[0] > footPos2[0]:
        footPos = footPos1
    else:
        footPos = footPos2
    return wheelPos, armPos, footPos

def draw(th, wheelPos, armPos, footPos, history):
    fig, ax = plt.subplots(figsize=(4,4))
    plt.axis('equal')
    ax.set(xlim=(-r2/np.sqrt(2), r1 + R1 + r2/np.sqrt(2)), ylim=(-r1-R1, r2))
    
    wheel = pch.Arc(footJoint, 2*r1, 2*r1, color='blue')
    ax.add_patch(wheel)

    arc = pch.Arc(armJoint, 2*r2, 2*r2, angle=-90,
                  theta1=-30, theta2=30, color='red')
    ax.add_patch(arc)

    pts = np.vstack((wheelPos, footPos, armPos))
    plt.plot(pts[:,0], pts[:,1], '-g')
    plt.plot(history[:,0], history[:,1], '-g')

    plt.scatter(wheelPos[0], wheelPos[1], c='blue', s=4)
    plt.scatter(armPos[0], armPos[1], c='red', s=4)
    plt.scatter(footPos[0], footPos[1], c='green', s=4)
    plt.savefig('frames/elliptical-{:.3f}.png'.format(th), bbox_inches='tight')
    plt.close(fig)

def cycle(phase, plot=True):
    history = []
    thrange = np.linspace(0, 2*np.pi, 40)
    for th in thrange:
        wheelPos, armPos, footPos = calcFootPos(th, np.pi/6*np.cos(th-phase))
        history += [footPos]
        if plot:
            draw(th, wheelPos, armPos, footPos, np.vstack(history))
    return thrange, np.vstack(history)

# Plot one cycle
thrange, history = cycle(0)
fig, ax = plt.subplots(figsize=(4,3))
plt.plot(thrange[1:-1], np.diff(history[:,0],2), '-r', label='x')
plt.plot(thrange[1:-1], np.diff(history[:,1],2), '-b', label='y')
plt.xlabel('theta')
plt.ylabel('accel')
plt.legend()
plt.savefig('accel.png', bbox_inches='tight')

# Plot shapes made by different phases
for phase in np.linspace(0, 2*np.pi, 40):
    thrange, history = cycle(phase, plot=False)
    fig, ax = plt.subplots(figsize=(4,4))
    plt.axis('equal')
    ax.set(xlim=(-r2/np.sqrt(2), r1 + R1 + r2/np.sqrt(2)), ylim=(-r1-R1, r2))
    plt.plot(history[:,0], history[:,1], '-g')
    plt.savefig('shapes/shape-{:.3f}.png'.format(phase), bbox_inches='tight')
    plt.close(fig)    
