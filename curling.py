from dash import Dash, dcc, html, Input, Output, callback, State, dash_table, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import os
import numpy as np
import random
from datetime import datetime
import requests
import ast

from geopy.geocoders import Photon

print("Insert season (in format XXXX):")
seasonNumber = input()

season = pd.read_csv('SeasonsCSV/'+ seasonNumber +'.csv')
    
season = season[season['Category'] != "QUA"]
season = season[season['Discipline'].isin(['Parallel Slalom', 'Slalom', 'Parallel GS', 'Parallel Giant Slalom', 'Giant Slalom'])]

season = season.iloc[: , 1:]
season = season.drop('Gender', axis=1)
season = season.drop_duplicates()
season['Date Formated'] = season.apply(lambda x: datetime.strptime(x['Date'],"%Y-%m-%d"), axis=1)
season.dropna()

# Curl request to get latitude and longitude from google
def getCoordinates(locationName):
    geolocator = Photon(user_agent="geoapiExercises")

    location = geolocator.geocode(locationName)
    if location == None:
        return None
    return location.latitude, location.longitude

# Getting weather for certain location and time
def getInfo(locationName, date):
    pack = getCoordinates(locationName)
    if pack != None:
        latitude, longitude = pack

        url = "https://meteostat.p.rapidapi.com/point/daily"
        querystring = {"lat":str(latitude),"lon":str(longitude),"start":date,"end":date}

        headers = {
            "x-rapidapi-key": "",
            "x-rapidapi-host": "meteostat.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring).json()
        if len(response['data']) > 0:
            return response['data'][0]['tmin'], response['data'][0]['tavg'], response['data'][0]['tmax'], response['data'][0]['wspd']
        return ()
    return ()

season['Info'] = season.apply(lambda x: getInfo(x['Location'], x['Date']), axis=1)

season['Info'] = season['Info'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
season = season[season['Info'].apply(lambda x: isinstance(x, (tuple, list)) and len(x) == 4)]

# Unpack the Info column into separate columns
season[['Temp Min', 'Temp Avg', 'Temp Max', 'Wind Speed']] = pd.DataFrame(season['Info'].to_list(), index=season.index)
season = season.drop(columns=['Info'])

season.to_csv("WeatherCSV/"+ seasonNumber +"Weather2023.csv", index=False)
