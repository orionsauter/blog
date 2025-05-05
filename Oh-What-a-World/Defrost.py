import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

kT0 = 1.0 #4.141947e-21 # J
W_melt = 334 # J/g
T_melt = 273
C_water = 4.184 # J/g/K
C_ice = 2.093 # J/g/K
k_water = 0.055575 # W/m/K https://www.engineeringtoolbox.com/water-liquid-gas-thermal-conductivity-temperature-pressure-d_2012.html
k_ice = 2.57 # W/m/K https://www.engineeringtoolbox.com/ice-thermal-properties-d_576.html
rho_water = 999.8 # kg/m^3
rho_ice = 919.4 # kg/m^3
Ti = 230 # K
P0 = 8e6
s = 0.10 # m
V0 = s**3

def LoadData(file):
    df = pd.read_csv(file, header=None, names=["time","W_kin"])
    df["sec"] = np.floor(df["time"])
    df["W_kin"] *= kT0
    df = df.groupby("sec").mean()
    return df

def Step(P, dt, V_ice, V_water, T_ice, T_water):
    m_ice = V_ice*rho_ice*1e3
    m_water = V_water*rho_water*1e3
    # Energy from microwave
    dE_ice = P*P0*dt*coef_ice*V_ice/V0
    dE_water = P*P0*dt*coef_water*V_water/V0
    # Conduction between phases
    dE_cond = (T_water-T_ice)*k_ice*dt*10
    dE_ice += dE_cond*m_water/m_ice
    dE_water -= dE_cond*m_water/m_ice
    # Heat water
    if m_water > 0:
        T_water += dE_water/C_water/m_water
    # Heat ice
    if T_ice < T_melt:
        T_ice += dE_ice/C_ice/m_ice
    # Melt ice
    elif m_ice > 0:
        m_melt = dE_ice/W_melt
        T_water = (T_water*m_water + T_melt*m_melt)/(m_water+m_melt)
        m_ice -= m_melt
        m_water += m_melt
    V_ice = m_ice/rho_ice*1e-3
    V_water = m_water/rho_water*1e-3
    return V_ice, V_water, T_ice, T_water

def Simulate(P, dt):
    t = np.arange(0.0, dt*n, dt)
    V_ice = np.empty_like(P)
    V_water = np.empty_like(P)
    T_ice = np.empty_like(P)
    T_water = np.empty_like(P)
    V_ice[0] = s**3
    V_water[0] = 0.0
    T_ice[0] = Ti
    T_water[0] = 273.0
    i = 0
    while i < len(P)-1 and V_ice[i] > 0:
        V_ice[i+1], V_water[i+1], T_ice[i+1], T_water[i+1] = Step(P[i], dt, V_ice[i], V_water[i], T_ice[i], T_water[i])
        i += 1
    df = pd.DataFrame(np.vstack([V_ice[:i+1], V_water[:i+1], T_ice[:i+1], T_water[:i+1]]).T,
                      index=t[:i+1], columns=["V_ice","V_water", "T_ice", "T_water"])
    return df

def PlotResult(df):
    fig, axs = plt.subplots(figsize=(4,4), nrows=2, sharex=True)
    axs[0].plot(df.index, df["V_ice"]*1e6, "-c", label="ice")
    axs[0].plot(df.index, df["V_water"]*1e6, "-b", label="water")
    axs[1].plot(df.index, df["T_ice"] - 273, "-c", label="ice")
    axs[1].plot(df.index, df["T_water"] - 273, "-b", label="water")
    axs[0].set_ylabel("vol. [ml]")
    axs[1].set_ylabel("temp. [deg C]")
    axs[1].set_xlabel("time")
    return fig, axs

if __name__ == "__main__":
    ice = LoadData("Ice.csv")
    water = LoadData("Water.csv")
    # coef_ice = np.polyfit(x=ice["time"], y=ice["W_kin"], deg=1)
    coef_ice = np.mean(ice["W_kin"]/ice["time"])
    f_ice = np.poly1d([coef_ice,0])
    # coef_water = np.polyfit(x=water["time"], y=water["W_kin"], deg=1)
    coef_water = np.mean(water["W_kin"]/water["time"])
    f_water = np.poly1d([coef_water,0])

    dt = 1.0
    n = 3600
    P = np.vstack([
        np.ones((n,)),
        np.hstack([0.5*np.ones((2*n//3,)),np.ones((n-2*n//3,))]),
        np.hstack([0.5*np.ones((n//2,)),np.ones((n-n//2,))]),
        np.hstack([0.5*np.ones((n//3,)),np.ones((n-n//3,))]),
        np.hstack([0.8*np.ones((n//2,)),np.ones((n-n//2,))]),
        np.hstack([0.2*np.ones((n//3,)),0.4*np.ones((n//3,)),0.6*np.ones((n//3,))])
    ])
    res = []
    for i in range(P.shape[0]):
        df = Simulate(P[i,:],dt)
        res += [df]

    Etot = []
    Ttot = []
    fig, ax = plt.subplots(figsize=(4,3))
    t = np.arange(0, dt*n, dt)
    cmap = mpl.colormaps["viridis"]
    for i in range(len(res)):
        Etot += [np.sum(P[i,:res[i].shape[0]])*dt]
        Ttot += [res[i].index[-1]]
    norm = mcolors.Normalize(np.min(Etot),np.max(Etot))
    for i in range(len(res)):
        plt.plot(t[:res[i].shape[0]], P[i,:res[i].shape[0]]-i*0.01, color=cmap(norm(Etot[i])))
    plt.xlabel("time")
    plt.ylabel("power")
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    plt.colorbar(sm, label="tot. energy", ax=ax)
    plt.savefig("power.png", bbox_inches="tight", dpi=100)
    
    minE = res[np.argmin(Etot)]
    fig, axs = PlotResult(minE)
    plt.suptitle(f"E = {np.min(Etot)}")
    plt.legend()
    plt.savefig("minE.png", bbox_inches="tight", dpi=100)
    maxE = res[np.argmax(Etot)]
    fig, axs = PlotResult(maxE)
    plt.suptitle(f"E = {np.max(Etot)}")
    plt.legend()
    plt.savefig("maxE.png", bbox_inches="tight", dpi=100)

    fig, axs = plt.subplots(figsize=(4,4), nrows=2)
    axs[0].plot(ice["time"],ice["W_kin"],"-")
    axs[0].plot(ice["time"],f_ice(ice["time"]),"--")
    axs[1].plot(water["time"],water["W_kin"],"-")
    axs[1].plot(water["time"],f_water(water["time"]),"--")
    axs[0].set_ylabel("E_kin ice")
    axs[1].set_ylabel("E_kin water")
    axs[1].set_xlabel("time")
    plt.savefig("xfer.png", bbox_inches="tight", dpi=100)