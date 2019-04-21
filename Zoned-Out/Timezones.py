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
    offset = str((timezone(zone).utcoffset(today).total_seconds()/3600 + 24) % 24)
    if offset in offsets:
        i = np.argwhere(np.array(offsets)==offset)[0,0]
        verts[i] = np.append(verts[i], lngs)
        zones[i] = np.append(zones[i], zone)
    else:
        offsets += [str(offset)]
        verts += [lngs]
        zones += [zone]
for i in range(len(zones)):
    width = (np.max(verts[i]) - np.min(verts[i]))*24/360
    widths += [width]

print(np.array([zones,offsets,widths]))
i = np.argmax(widths)
print(zones[i],offsets[i],widths[i])
i = np.argmin(widths)
print(zones[i],offsets[i],widths[i])
    
