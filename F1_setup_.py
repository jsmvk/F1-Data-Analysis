#!/usr/bin/env python
# coding: utf-8

# In[2]:


import fastf1 as ff1
from fastf1 import utils
from fastf1 import plotting
from fastf1 import legacy


# In[39]:


from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
import numpy as np
import pandas as pd
import os
import seaborn as sns
from datetime import datetime
from datetime import timedelta
from fastf1.core import Laps


# In[4]:


ff1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme='fastf1', misc_mpl_mods=True)


# In[5]:


os.getcwd()
os.chdir('C:/Users/jsmvk/Desktop/projects/Lic')


# In[6]:


ff1.Cache.enable_cache('cache')


# In[28]:


def telemetry(year, race, session, driver_1, driver_2):
    
    session = ff1.get_session(year, race, session)
    session.load()

    fast_driver_1 = session.laps.pick_driver(driver_1).pick_fastest()
    driver_1_car_data = fast_driver_1.get_car_data()
    
    fast_driver_2 = session.laps.pick_driver(driver_2).pick_fastest()
    driver_2_car_data = fast_driver_2.get_car_data()
    
    delta_time, ref_tel, compare_tel = utils.delta_time(fast_driver_1, fast_driver_2)
    
    speed_1 = driver_1_car_data['Speed']
    time_1 = driver_1_car_data['Time']
    throttle_1 = driver_1_car_data['Throttle']
    
    time_2 = driver_2_car_data['Time']
    throttle_2 = driver_2_car_data['Throttle']
    speed_2 = driver_2_car_data['Speed']
    
    fig, ax = plt.subplots(3)
    fig.set_size_inches(20, 10)
    
    ax[0].plot(time_1, speed_1, label = driver_1, color = ff1.plotting.driver_color(driver_1))
    ax[0].plot(time_2, speed_2, label = driver_2, color = ff1.plotting.driver_color(driver_2))
    ax[0].set_ylabel('Speed [km/h]')
    ax[0].set_title(f'{year} {race} GP {session}')
    ax[0].legend(loc = 'lower right')
    
    ax[1].plot(time_1, throttle_1, label = driver_1, color = ff1.plotting.driver_color(driver_1))
    ax[1].plot(time_2, throttle_2, label = driver_2, color = ff1.plotting.driver_color(driver_2))
    ax[1].set_xlabel('Time')
    ax[1].set_ylabel('Throttle')
    ax[1].legend(loc = 'lower right')
    
    ax[2].plot(ref_tel['Distance'], delta_time)
    ax[2].axhline(0)
    ax[2].set_ylabel(f'<-- {driver_2} ahead | {driver_1} ahead -->(s)')
    
    plt.show()


# In[9]:


def pole_gap(year, race, session):

    session = ff1.get_session(year, race, session)
    session.load()
    
    drivers = pd.unique(session.laps['Driver'])
    
    list_fastest_laps = list()

    for drv in drivers:
        drvs_fastest_lap = session.laps.pick_driver(drv).pick_fastest()
        list_fastest_laps.append(drvs_fastest_lap)

    fastest_laps = Laps(list_fastest_laps).sort_values(by='LapTime').reset_index(drop=True)

    pole_lap = fastest_laps.pick_fastest()
    fastest_laps['LapTimeDelta'] = ((fastest_laps['LapTime'] - pole_lap['LapTime']) / pole_lap['LapTime']) * 100

    team_colors = list()

    for index, lap in fastest_laps.iterlaps():
        color = ff1.plotting.team_color(lap['Team'])
        team_colors.append(color)
        
    fig, ax = plt.subplots()
    fig.set_size_inches(15, 10)
    
    ax.barh(fastest_laps.index, fastest_laps['LapTimeDelta'],
            color=team_colors, edgecolor='grey')
    ax.set_yticks(fastest_laps.index)
    ax.set_yticklabels(fastest_laps['Driver'])
    ax.invert_yaxis()
    ax.set_title(f'{year} {race} {ses} \n Gap to best lap (%)')


# In[142]:


def session_pace(year, race, session, driver_1, driver_2, driver_3):
    if session == 'Q':
        ses = 'Qualifying'
    elif session == 'R':
        ses = 'Race'
    elif session == 'S':
        ses = 'Sprint'
    else:
        ses = 'Practice'
    
    session = ff1.get_session(year, race, session)
    session.load()
    
    fast_driver_1 = session.laps.pick_driver(driver_1).pick_quicklaps(1.03)
    fast_driver_2 = session.laps.pick_driver(driver_2).pick_quicklaps(1.03)
    fast_driver_3 = session.laps.pick_driver(driver_3).pick_quicklaps(1.03)
    
    fig, ax = plt.subplots()
    fig.set_size_inches(15, 10)
    
    def fuel_corrected_lap_time(original_lap_time, lap_number):
        fuel_correction_time = (57 - lap_number) * 65  # Calculate fuel correction time
        fuel_correction_timedelta = timedelta(milliseconds=fuel_correction_time)
        corrected_lap_time = original_lap_time - fuel_correction_timedelta
        return corrected_lap_time

    
    drivers = [{'name': driver_1, 'data': fast_driver_1},
               {'name': driver_2, 'data': fast_driver_2},
               {'name': driver_3, 'data': fast_driver_3}]
    
    for driver in drivers:
        lap_times = driver['data']['LapTime']
        corrected_lap_times = [fuel_corrected_lap_time(lt, ln) for ln, lt in enumerate(lap_times, start=1)]
        ax.plot(range(1, len(lap_times) + 1), corrected_lap_times, marker='o', label=driver['name'])

    ax.set_xlabel('Lap Number')
    ax.set_ylabel('Fuel-corrected Lap Time')
    ax.set_title(f'{year} {race} {ses} quickest lap times (fuel-corrected)')
    ax.legend(loc='lower right')

    plt.show()


# In[151]:


def race_trace(year, race):
    session = ff1.get_session(year, race, 'R')
    session.load()
    
    fig, ax = plt.subplots(figsize=(8.0, 4.9))
    
    for drv in session.drivers:
        drv_laps = session.laps.pick_driver(drv)
        ax.plot(drv_laps['LapNumber'], drv_laps['Position'])
    
    ax.set_ylim([20.5, 0.5])
    ax.set_yticks([1, 5, 10, 15, 20])
    ax.set_xlabel('Lap')
    ax.set_ylabel('Position')
    
    ax.legend(bbox_to_anchor=(1.0, 1.02))
    plt.tight_layout()

    plt.show()


# In[98]:


race_trace(2022, 'Monza', 'R', 'VER')
telemetry(2022, 'Monza', 'Qualifying', 'RUS', 'VER')
pole_gap(2023, 'Bahrain', 'Q')
session_pace(2023, 'Miami', 'R', 'VER', 'ALO', 'HAM')
race_trace(2022, 'Miami')





