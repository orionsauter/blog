import timezonefinder as tz
from pytz import timezone
import pytz
from datetime import datetime
import numpy as np

#arcticCirc = 66.5608
# Antarctica dips outside this, so extend a bit
arcticCirc = 64

tf = tz.TimezoneFinder()
today = datetime.now()

widths = []
zones = []
offsets = []
verts = []
nbrs = []
rates = []

# Consolidate timezones
for zone in pytz.common_timezones:
    try:
        geo = np.array(tf.get_geometry(tz_name=zone))
    except:
        # Skip unrecognized timezones
        continue
    # Skip timezones with the wrong format
    if (len(geo.shape) != 4 or geo.shape[2] != 2):
        continue
    lngs = geo[:,:,0,:].flatten()
    lats = geo[:,:,1,:].flatten()
    lngs = lngs[np.abs(lats) < arcticCirc]
    if len(lngs) < 1:
        # Skip timezones entirely in the arctic
        continue
    offset = (timezone(zone).utcoffset(today).total_seconds()/3600 + 24) % 24
    i = np.argwhere(np.array(offsets)==offset)
    if len(i) > 0:
        i = i[0,0]
        verts[i] = np.append(verts[i], lngs)
        zones[i] = np.append(zones[i], zone)
    else:
        offsets += [offset]
        verts += [lngs]
        zones += [zone]
for i in range(len(zones)):
    width = (np.max(verts[i]) - np.min(verts[i]))*24/360
    widths += [width]
    neighbors = []
    for j in range(len(zones)):
        if i==j:
            continue
        if len(set(verts[i]) & set(verts[j])) != 0:
            neighbors += [float(offsets[j])]
    nbrs += [neighbors]
    if len(neighbors) > 0:
        rates += [max(abs(np.array(neighbors)-float(offsets[i])))/width]
    else:
        rates += [0]

#print(np.array([zones,offsets,widths,rates]))
i = np.argmax(widths)
print(zones[i],offsets[i],widths[i],nbrs[i],rates[i])
i = np.argmin(widths)
print(zones[i],offsets[i],widths[i],nbrs[i],rates[i])
print(np.array(zones)[np.array(offsets) % 1 != 0])
    
