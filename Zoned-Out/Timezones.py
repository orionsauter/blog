import timezonefinder as tz
from pytz import timezone
import pytz
from datetime import datetime
import numpy as np

#arcticCirc = 66.5608
# Antarctica dips outside this, so extend a bit
arcticCirc = 65

tf = tz.TimezoneFinder()

maxWidth = 0
widest = ""

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
    width = np.max(lngs) - np.min(lngs)
    if width > maxWidth:
        maxWidth = width
        widest = zone

print(widest + ": " + str(maxWidth*24/360))
    
