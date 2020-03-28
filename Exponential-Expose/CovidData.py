import os
import requests as req
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

months = mdates.MonthLocator()  # every month
days = mdates.DayLocator()  # every day
months_fmt = mdates.DateFormatter('%b')
pd.plotting.register_matplotlib_converters()

# Load data if it exists
if os.path.exists('covid.pkl'):
    data = pd.read_pickle('covid.pkl')
# Fetch it otherwise
else:
    resp = req.get('https://covid19api.herokuapp.com/confirmed')
    locations = resp.json()['locations']
    idxUS = [i for i in range(len(locations))
             if locations[i]['country'] == 'US'][0]
    data = pd.DataFrame([[datetime.strptime(date,"%m/%d/%y").date(),
                          locations[idxUS]['history'][date],
                          np.sum([locations[i]['history'][date]
                                  for i in range(len(locations))])]
                         for date in locations[idxUS]['history'].keys()])
    data[0] = pd.to_datetime(data[0])
    data.to_pickle('covid.pkl')

# Sort by date
data.sort_values(0, inplace=True)
delta = np.diff(data[1])
n = data[1][0:-1]
XX = np.array(n[delta > 0], ndmin=2).T
# Fit line through 0
fit = np.linalg.lstsq(XX, delta[delta > 0], rcond=None)[0]
eqn = "y = {:.2g} x".format(fit[0])

fig, ax = plt.subplots(figsize=(4,3))
ax.xaxis.set_major_locator(months)
ax.xaxis.set_minor_locator(days)
ax.xaxis.set_major_formatter(months_fmt)
plt.plot(data[0], data[1], '-')
plt.xlabel('date')
plt.ylabel(r'$N_{US}$')
fig.autofmt_xdate()
plt.savefig('US time.png', bbox_inches='tight')

fig, ax = plt.subplots(figsize=(4,3))
plt.plot(data[1], data[2], '-')
plt.xlabel(r'$N_{US}$')
plt.ylabel(r'$N_{tot}$')
plt.savefig('US World.png', bbox_inches='tight')

fig, ax = plt.subplots(figsize=(4,3))
plt.plot(n[delta > 0], delta[delta > 0], '.')
plt.plot(n[delta > 0], n[delta > 0]*fit[0], '-r',
         alpha=0.5, linewidth=2)
plt.text(0.05, 0.90, eqn, transform=ax.transAxes, fontsize=14)
plt.xlabel(r'$N_{US}$')
plt.ylabel(r'$\dot{N}_{US}$')
plt.savefig('US diff.png', bbox_inches='tight')


