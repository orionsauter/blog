import numpy as np
import matplotlib.pyplot as plt

V_tot = 1e-3 # m^3 = 1 L
a = 0.19 # m = 7.5"
b = 0.11 # m = 4.25"
h = 0.16 # m = 6.25"
A = np.pi*a*b
n = 60

plt.figure(figsize=(4,4))
for V_bot in np.linspace(0, V_tot, n)[1:-1]:
    V_top = V_tot - V_bot
    z0_bot = V_bot/A
    z0_top = V_top/A
    theta_max = np.pi/4
    x = np.linspace(0, theta_max, n)
    sine_x = np.sin(x)
    CM_bot = (A/4)*np.array([a*a*sine_x,
                             0,
                             a*a*sine_x*sine_x + 4*z0_bot*z0_bot])/V_bot
    CM_top = (A/4)*np.array([a*a*sine_x,
                             0,
                             a*a*sine_x*sine_x + 4*z0_top*z0_top])/V_top
    CM_top[2] += h
    CM = (CM_bot*V_bot + CM_top*V_top)/V_tot
    phi = np.arctan2(CM[2], a - CM[0])
    plt.clf()
    plt.plot(x*180/np.pi, (x+phi)*180/np.pi, '-')
    plt.hlines(90, 0, theta_max*180/np.pi, linestyles="dotted")
    plt.ylim((0, 180))
    plt.xlabel("tip angle (deg)")
    plt.ylabel("center of mass angle (deg)")
    plt.title("{:.0f}% drained".format(V_bot/V_tot*100))
    plt.savefig("frames/pitcher-{:.0f}.png".format(V_bot/V_tot*100),
                bbox_inches="tight")
