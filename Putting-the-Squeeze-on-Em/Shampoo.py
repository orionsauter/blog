import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as pch
from scipy.integrate import quad
from scipy.optimize import minimize

def p_integrand(th, a, b):
    e = np.sqrt(a*a-b*b)/a
    return 4*a*np.sqrt(1.0 - e*e*np.sin(th)**2)

def perimeter(a, b):
    if (a < b):
        a, b = b, a
    P, err = quad(p_integrand, 0.0, 0.5*np.pi, args=(a, b))
    return P

avec = [1.0, 2.5, 4.0]
na = len(avec)
b = 1.0
n = 20
drange = 0.1
A = np.array([np.pi*a*b for a in avec])
P = [perimeter(a, b) for a in avec]
da = np.linspace(-drange, drange, n)
dA = np.zeros((n,na))
fig = plt.figure(figsize=(4,4))
ax = fig.add_subplot(aspect="equal")
for i in range(n):
    plt.cla()
    for ai in range(na):
        a = avec[ai]
        anew = a + da[i]
        bnew = minimize(lambda bp: np.abs(perimeter(anew,bp)-P[ai]), b).x[0]
        dA[i,ai] = np.pi*anew*bnew - A[ai]
        if ai == 1:
            asave = anew
            bsave = bnew
    a = avec[1]
    ell = pch.Ellipse(xy=[0,0], width=2*asave, height=2*bsave,
                      fill=False, edgecolor="red")
    ell0 = pch.Ellipse(xy=[0,0], width=2*a, height=2*b,
                      fill=False, edgecolor="blue")
    ax.add_artist(ell)
    ax.add_artist(ell0)
    plt.xlim((-a-drange, a+drange))
    plt.ylim((-a-drange, a+drange))
    plt.title(r"$\Delta A = {:.2f}$".format(dA[i,1]))
    plt.savefig("frames/squeeze-{}.png".format(i), bbox_inches="tight")
    plt.savefig("frames/squeeze-{}.png".format(39-i), bbox_inches="tight")

fig, ax = plt.subplots(figsize=(4,4))
for i in range(na):
    dP = A[i]/(A[i]+dA[:,i]) - 1.0
    plt.plot(da, dP, '-', label=avec[i])
plt.xlabel("width change")
plt.ylabel("pressure change")
plt.legend(title=r"$a_0$")
plt.savefig("pressure.png", bbox_inches="tight")
