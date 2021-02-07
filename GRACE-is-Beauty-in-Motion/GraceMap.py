import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, shiftgrid
from datetime import date
import pydap.client

def draw_map(m, lons, lats, lwe, clevs):
    m.drawcoastlines()
    x, y = m(lons, lats)
    cs = m.contourf(x, y, lwe, clevs, cmap=plt.cm.bwr)

# Get data from JPL
url = "https://podaac-opendap.jpl.nasa.gov/opendap/allData/tellus/L3/mascon/RL06/JPL/v02/CRI/netcdf/GRCTellus.JPL.200204_202011.GLO.RL06M.MSCNv02CRI.nc"
data = pydap.client.open_url(url)
t0 = date.fromisoformat("2002-01-01").toordinal()

# Set up Mollewide projection
fig, ax = plt.subplots(figsize=(4,4))
m = Basemap(projection='moll', lon_0=0, lat_0=0)

print("Loading times...")
times = [date.fromordinal(int(t0 + t)) for t in data["time"][:].data]
print("Loading LWEs...")
lwe = np.array(data["lwe_thickness"].data[0])
print("Loading coords...")
lons_orig = data["lon"][:].data
lats_orig = data["lat"][:].data
# Center of Northern Atlantic
cent_lon = np.argmin(np.abs(lons_orig+39.756055))
cent_lat = np.argmin(np.abs(lats_orig-35.693924))
nlvl = 40
# Use color range between 5th and 95th percentile
clevs = np.linspace(np.quantile(lwe, 0.05),
                    np.quantile(lwe, 0.95), nlvl)
for i in range(len(times)):
    # Grid starts at lon = 0, so shift
    lwe_plot, lons_flat = shiftgrid(180., lwe[i,:,:],
                                    lons_orig,
                                    start=False)
    lons, lats = np.meshgrid(lons_flat, lats_orig)
    plt.cla()
    draw_map(m, lons, lats, lwe_plot, clevs)
    if i == 0:
        # Only need to draw colorbar once
        cbar = m.colorbar(None, location='bottom', pad="5%")
        cbar.ax.set_xticklabels(cbar.ax.get_xticklabels(), rotation=-45)
        cbar.set_label("Liquid Water Eq. Thickness (cm)")
    plt.title(times[i].strftime("%b %Y"))
    plt.savefig("frames/map-{}.png".format(i))

# Depth at Northern Atlantic
fig, ax = plt.subplots(figsize=(4,4))
plt.plot(times, lwe[:,cent_lon,cent_lat], '-')
plt.xlabel("date")
plt.ylabel("water depth deviation (cm)")
fig.autofmt_xdate()
plt.savefig("depth.png")
