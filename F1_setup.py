import fastf1 as ff1
from fastf1 import utils
from fastf1 import plotting
from fastf1 import legacy
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
import numpy as np
import pandas as pd
import os
import seaborn as sns
from fastf1.core import Laps

ff1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme='fastf1', misc_mpl_mods=True)

os.getcwd()
os.chdir('C:/Users/jsmvk/Desktop/projects/Lic')

ff1.Cache.enable_cache('cache')

def telemetry(year, race, session, driver_1, driver_2):
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
    ax[0].set_title(f'{year} {race} GP {ses}')
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

def pole_gap(year, race, session):
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
    
    drivers = pd.unique(session.laps['Driver'])
    
    list_fastest_laps = list()

    for drv in drivers:
        drvs_fastest_lap = session.laps.pick_driver(drv).pick_fastest()
        list_fastest_laps.append(drvs_fastest_lap)

    fastest_laps = Laps(list_fastest_laps).sort_values(by='LapTime').reset_index(drop=True)

    pole_lap = fastest_laps.pick_fastest()
    fastest_laps['LapTimeDelta'] = fastest_laps['LapTime'] - pole_lap['LapTime']

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
    ax.set_title(f'{year} {race} {ses} \n Gap to best lap (s)')

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
    
    fast_driver_1 = session.laps.pick_driver(driver_1).pick_quicklaps()
    fast_driver_2 = session.laps.pick_driver(driver_2).pick_quicklaps()
    fast_driver_3 = session.laps.pick_driver(driver_3).pick_quicklaps()
    
    fig, ax = plt.subplots()
    fig.set_size_inches(15, 10)
    
    ax.plot(fast_driver_1['LapNumber'], fast_driver_1['LapTime'], label = driver_1, marker = 'o', 
            color = ff1.plotting.driver_color(driver_1))
    ax.plot(fast_driver_2['LapNumber'], fast_driver_2['LapTime'], label = driver_2, marker = 'o', 
            color = ff1.plotting.driver_color(driver_2))
    ax.plot(fast_driver_3['LapNumber'], fast_driver_3['LapTime'], label = driver_3, marker = 'o', 
            color = ff1.plotting.driver_color(driver_3))
    ax.set_xlabel('Lap Number')
    ax.set_ylabel('Lap Time')
    ax.set_title(f'{year} {race} {ses} quickest lap times')
    ax.legend(loc = 'lower right')
    
def race_trace(year, race, session, driver_1):
    session = ff1.get_session(year, race, session)
    session.load()
    
    # x = lap
    # y = position
    # hue = driver
    
    driver = session.laps.pick_driver(driver_1)
    pos = driver.get_car_data()
    
    #print(pos['Time'])
    
    #fig, ax = plt.subplots()
    #fig.set_size_inches(5, 10)


# In[10]:


race_trace(2022, 'Monza', 'R', 'VER')
telemetry(2022, 'Monza', 'Q', 'RUS', 'VER')
pole_gap(2022, 'Monza', 'Q')
session_pace(2022, 'Belgium', 'R', 'VER', 'RUS', 'LEC')
