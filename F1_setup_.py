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
import plotly.express as plx
from datetime import datetime
from datetime import timedelta
from fastf1.core import Laps

ff1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme='fastf1', misc_mpl_mods=True)

os.getcwd()
os.chdir('C:/Users/jsmvk/Desktop/projects/Lic')

ff1.Cache.enable_cache('cache')

session_mapping = {
    'Q': 'Qualifying',
    'R': 'Race',
    'S': 'Sprint',
    'FP1': 'FP1',
    'FP2': 'FP2',
    'FP3': 'FP3'}


def telemetry(year, race, session, driver_1, driver_2):
    
    full_session_name = session_mapping.get(session, 'NA')
    
    session = ff1.get_session(year, race, session)
    session.load()

    fig, ax = plt.subplots(3)
    fig.set_size_inches(20, 10)

    drivers_data = []
    
    for driver_name in [driver_1, driver_2]:
        fast_driver = session.laps.pick_driver(driver_name).pick_fastest()
        driver_car_data = fast_driver.get_car_data()
        drivers_data.append({'name': driver_name, 'data': fast_driver, 'car_data': driver_car_data})
    
    delta_time, ref_tel, compare_tel = utils.delta_time(drivers_data[0]['data'], drivers_data[1]['data'])
    
    for driver in drivers_data:
        driver_name = driver['name']
        driver_car_data = driver['car_data']

        speed = driver_car_data['Speed']
        time = driver_car_data['Time']
        throttle = driver_car_data['Throttle']

        ax[0].plot(time, speed, label = driver_name, color = ff1.plotting.driver_color(driver_name))
        ax[1].plot(time, throttle, label = driver_name, color = ff1.plotting.driver_color(driver_name))

    ax[0].set_ylabel('Speed [km/h]')
    ax[0].set_title(f'{year} {race} GP {full_session_name}')
    ax[0].legend(loc = 'lower right')

    ax[1].set_xlabel('Time')
    ax[1].set_ylabel('Throttle')
    ax[1].legend(loc = 'lower right')
    
    ax[2].plot(ref_tel['Distance'], delta_time)
    ax[2].axhline(0)
    ax[2].set_ylabel(f'<-- {driver_2} ahead | {driver_1} ahead -->(s)')
    
    plt.show()


def pole_gap(year, race, session):

    full_session_name = session_mapping.get(session, 'NA')
    
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
    ax.set_title(f'{year} {race} {full_session_name} \n Gap to best lap (%)')

def fuel_corrected_lap_time(original_lap_time, lap_number, max_lap_number):
        fuel_correction_time = (max_lap_number - lap_number) * 65 # formula source: https://www.reddit.com/r/F1Technical/comments/11oskuy/computation_of_fuelcorrected_lap_time/
        fuel_correction_timedelta = timedelta(milliseconds=fuel_correction_time)
        corrected_lap_time = original_lap_time - fuel_correction_timedelta
        return corrected_lap_time

def session_pace(year, race, session, driver_1, driver_2):

    full_session_name = session_mapping.get(session, 'NA')
    
    session = ff1.get_session(year, race, session)
    session.load()
    
    fig, ax = plt.subplots()
    fig.set_size_inches(15, 10)
    
    drivers_data = [{'name': driver_1}, {'name': driver_2}]
                    
    for driver in drivers_data:
        fast_laps = session.laps.pick_driver(driver['name']).pick_quicklaps(1.06) # Return all laps with LapTime faster than threshold
        driver['data'] = fast_laps
        lap_times = driver['data']['LapTime']
        max_lap_number = len(lap_times) + 1
        corrected_lap_times = [fuel_corrected_lap_time(lt, ln, max_lap_number) for ln, lt in enumerate(lap_times, start=1)]
        ax.plot(range(1, len(lap_times) + 1), corrected_lap_times, label=driver['name'])

    ax.set_xlabel('Lap Number')
    ax.set_ylabel('Fuel-corrected Lap Time')
    ax.set_title(f'{year} {race} {full_session_name} quickest lap times (fuel-corrected)')
    ax.legend(loc='lower right')

    plt.show()

compound_color = {'HARD': '#f0f0ec', 
                      'INTERMEDIATE': '#43b02a', 
                      'MEDIUM': '#ffd12e', 
                      'SOFT': '#da291c',  
                      'WET': '#0067ad'}

def tyre_strategy(year, race, session):
    
    full_session_name = session_mapping.get(session, 'NA')
    
    session = ff1.get_session(year, race, session)
    session.load()
    laps = session.laps

    fig, ax = plt.subplots(figsize=(15, 10))
    
    drivers = pd.unique(session.laps['Driver'])

    stints = laps[['Driver', 'Stint', 'Compound', 'LapNumber']]
    stints = stints.groupby(['Driver', 'Stint', 'Compound'])
    stints = stints.count().reset_index()
    stints = stints.rename(columns={'LapNumber': 'StintLength'})
    
    for driver in drivers:
        driver_stints = stints.loc[stints['Driver'] == driver]
        previous_stint_end = 0
        
        for idx, row in driver_stints.iterrows():
            
            plt.barh(y = driver,
                width = row['StintLength'],
                left = previous_stint_end, # start of horizontal bar - new stint
                color = compound_color[row['Compound']],
                edgecolor = 'black',
                fill = True)

            previous_stint_end += row['StintLength']

    plt.title(f'{year} {race} {full_session_name} tyre strategies')
    plt.xlabel('Lap Number')
    
    legend_handles = [Line2D([0], [0], marker='o', label=key, markerfacecolor=value, markersize=10) for key, value in compound_color.items()] #Line2D creates legend visuals
    legend_labels = list(compound_color.keys())
    
    plt.legend(handles=legend_handles, labels=legend_labels, loc='lower right', title='Compounds')
    ax.invert_yaxis()

    plt.tight_layout()
    plt.show()

def top_speed(year, race, session): # works but colors for teams are not correct
    full_session_name = session_mapping.get(session, 'NA')
    
    session = ff1.get_session(year, race, session)
    session.load()

    fig, ax = plt.subplots()
    fig.set_size_inches(20, 10)
    
    drivers = pd.unique(session.laps['Driver'])
    
    drivers_data = []
    
    for i in drivers:
        fast_driver = session.laps.pick_driver(i).pick_fastest()
        drivers_data.append({'name': i, 'data': fast_driver})
        
     for driver in drivers_data:
        laps_best = driver['data']
    
    laps_best_detail = [driver['data'] for driver in drivers_data]
    laps_best_detail = pd.DataFrame(laps_best_detail)
    
    laps_best = ['LapTime', 'Team', 'Driver', 'SpeedST']
    laps_best = pd.DataFrame(laps_best_detail[laps_best])
    laps_best.reset_index(inplace = True)
    laps_best = laps_best.drop(['index'], axis = 1)
    
    aggregations = {
    'LapTime': 'min',          
    'SpeedST': 'first'}
    
    laps_best_team = laps_best.groupby('Team').agg(aggregations)
    
    laps_best_team = pd.DataFrame(laps_best_team)
    laps_best_team = laps_best_team.sort_values(by = 'LapTime')
    laps_best_team.rename(columns = {'SpeedST': 'Max_Speed'}, inplace = True)

    fastest = laps_best_team.iloc[0, 0]
    laps_best_team['Delta'] = laps_best_team['LapTime'] - fastest # for every driver lap time minus session fastest lap
    laps_best_team['Delta'] = laps_best_team['Delta'] / np.timedelta64(1, 's')
    laps_best_team.reset_index(inplace = True)
    
    fig = px.scatter(laps_best_team, x = 'Max_Speed', y = 'Delta', text = 'Team', color = 'Team')
    fig.update_layout(plot_bgcolor = 'rgb(220, 220, 220)')
    fig.update_layout(font_color = 'rgb(70, 70, 70)')
    fig.update_layout(title = f'{full_session_name} {year} {race} <br> lap times delta to best lap', title_x = 0.5)
    fig.update_layout(yaxis_title = 'Delta (s)', xaxis_title = 'Max Speed (kph)')
    fig.show()

def race_gaps(year, race, session): # plot base - to be upgraded
    
    full_session_name = session_mapping.get(session, 'NA')
    
    session = ff1.get_session(year, race, session)
    session.load()

    fig, ax = plt.subplots()
    fig.set_size_inches(15, 10)
    
    drivers = pd.unique(session.laps['Driver'])
    
    drivers_data = []
    
    for drv in drivers:
        drvs_qlaps = session.laps.pick_driver(drv).pick_quicklaps()
        drivers_data.append({'name': drv, 'data': drvs_qlaps})
       
    for i in range(len(drivers_data) - 1):
        drivers_data_1 = drivers_data[i]['data']
        drivers_data_2 = drivers_data[i + 1]['data']
        delta_time, ref_tel, compare_tel = utils.delta_time(drivers_data_1, drivers_data_2)
        lap_numbers = drivers_data_1['LapNumber']
        
        min_length = min(len(lap_numbers), len(delta_time))
        lap_numbers = lap_numbers[:min_length]
        delta_time = delta_time[:min_length]
        
        ax.plot(lap_numbers, delta_time) 
        
    ax.axhline(0)
    ax.set_ylabel(f'<-- drv ahead | drv ahead -->(s)')
    
    plt.show()
