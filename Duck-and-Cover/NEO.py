import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import astropy
import astropy.units as u
from matplotlib.animation import FuncAnimation
from tqdm import tqdm
from poliastro.bodies import Earth, Mars, Venus, Sun
from poliastro.twobody import Orbit, angles
from poliastro.util import norm, time_range
from poliastro.ephem import Ephem
from poliastro.frames import Planes
from poliastro.maneuver import Maneuver

# https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html#/?sstr=2024%20YR4&view=VOPC
neo = pd.DataFrame({"Value": [0.6641470047,2.539140658,0.8527779956,3.452810058,271.4123332,
                              134.6421989,351.0756547,1477.843910783575,0.2435981211,4.225503321],
                    "Uncert": [0.000024804,0.00017633,0.0000037604,0.000089566,0.000021691,
                               0.00013518,0.00086942,0.15394,0.000025375,0.00029344],
                    "Unit": [u.one,u.au,u.au,u.deg,u.deg,u.deg,u.deg,u.day,u.deg/u.day,u.au]},
                   index=["e","a","q","i","node","peri","M","period","n","Q"])

def GetVari(orb, mag, phi, th):
    # Apply impulse to change orbit
    man = Maneuver.impulse([mag*np.cos(phi)*np.sin(th),mag*np.sin(phi)*np.sin(th),mag*np.cos(th)] << u.km / u.s)
    return orb.apply_maneuver(man)

if __name__ == "__main__":
    nvar = 300 # Number of variations
    orb = Orbit.from_sbdb("2024 YR4")
    # Center on estimated impact
    t0 = astropy.time.Time("2032-12-22", format="isot", scale="tdb")
    epochs = time_range(
        t0 - astropy.time.TimeDelta(2 * u.year),
        end=t0 + astropy.time.TimeDelta(2 * u.year),
        periods=int(4*u.year/(3 * u.day))
    )
    astrd = Ephem.from_orbit(orb, epochs, plane=Planes.EARTH_ECLIPTIC)
    rng = np.random.default_rng()
    # Perturb by 10% initial velocity
    dv = 0.1*np.sqrt(np.sum(astrd.rv(epochs[0])[1]**2))
    print(dv)
    coefs = rng.random((nvar, 3))
    # coefs[:,0] = coefs[:,0]*dv
    coefs[:,0] = rng.normal(0,dv.to("km/s").value,size=(nvar,))
    coefs[:,1] *= 2*np.pi
    coefs[:,2] *= np.pi
    varis = [Ephem.from_orbit(GetVari(orb,*coefs[i,:]), epochs, plane=Planes.EARTH_ECLIPTIC) for i in range(coefs.shape[0])]
    earth = Ephem.from_body(Earth, epochs, plane=Planes.EARTH_ECLIPTIC)
    distance = np.array([(norm(astrd.rv(ep)[0] - earth.rv(ep)[0]) - Earth.R).to("km").value for ep in epochs])
    vari_d = np.array([[(norm(vari.rv(ep)[0] - earth.rv(ep)[0]) - Earth.R).to("km").value for ep in epochs] for vari in tqdm(varis)])
    t = epochs.to_value('mjd', 'long')

    fig, ax = plt.subplots(figsize=(4,3))
    for i in rng.choice(len(varis), size=100, replace=False):
        plt.plot(t, vari_d[i,:], "--")
    plt.plot(t, distance, "-k")
    plt.xlabel("MJD [days]")
    plt.ylabel("distance [km]")
    plt.tight_layout()
    plt.savefig("dseries.png", dpi=100)

    min0 = np.min(distance)
    fig, ax = plt.subplots(figsize=(4,3))
    plt.hist(np.min(vari_d,axis=1)-min0,bins=50)
    ylim = plt.ylim()
    plt.vlines(-min0, *ylim, linestyles="dotted", colors="red")
    plt.ylim(ylim)
    plt.xlabel("distance diff. [km]")
    plt.ylabel("count")
    plt.tight_layout()
    plt.savefig("dhist.png", dpi=100)

    mars = Ephem.from_body(Mars, epochs, plane=Planes.EARTH_ECLIPTIC)
    venus = Ephem.from_body(Venus, epochs, plane=Planes.EARTH_ECLIPTIC)
    sun = Ephem.from_body(Sun, epochs, plane=Planes.EARTH_ECLIPTIC)
    astrd_r = np.vstack([astrd.rv(ep)[0].to("km").value for ep in epochs])
    earth_r = np.vstack([earth.rv(ep)[0].to("km").value for ep in epochs])
    mars_r = np.vstack([mars.rv(ep)[0].to("km").value for ep in epochs])
    venus_r = np.vstack([venus.rv(ep)[0].to("km").value for ep in epochs])
    fig, ax = plt.subplots(figsize=(4,4))
    plt.plot(earth_r[:,0],earth_r[:,1],"-b")
    plt.plot(mars_r[:,0],mars_r[:,1],"-r")
    plt.plot(venus_r[:,0],venus_r[:,1],"-c")
    plt.plot(astrd_r[:,0],astrd_r[:,1],"-m")
    plt.plot(*sun.rv(epochs[0])[0].to("km").value[:2],".y")
    edot, = plt.plot(earth_r[[0],0],earth_r[[0],1],".b")
    mdot, = plt.plot(mars_r[[0],0],mars_r[[0],1],".r")
    vdot, = plt.plot(venus_r[[0],0],venus_r[[0],1],".c")
    adot, = plt.plot(astrd_r[[0],0],astrd_r[[0],1],".m")
    def animate(i):
        edot.set_data(earth_r[[i],0],earth_r[[i],1])
        mdot.set_data(mars_r[[i],0],mars_r[[i],1])
        vdot.set_data(venus_r[[i],0],venus_r[[i],1])
        adot.set_data(astrd_r[[i],0],astrd_r[[i],1])
        ttl = ax.set_title(epochs[i].to_value("isot","date"))
        return edot, mdot, vdot, adot, ttl
    ani = FuncAnimation(fig, animate, range(0, astrd_r.shape[0], 2), blit=True, interval=50)
    ani.save("orbit.gif", writer="ffmpeg", fps=100, dpi=100)
