from dash import Dash, dcc, html, Input, Output, callback, State, dash_table, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import os
import numpy as np
import random
from datetime import datetime
import pyarrow as pa
import pyarrow.parquet as pq
import glob

# Formated athletes data
arrow = pq.read_table("AthletesCSV/allathletes.parquet")
athletes = arrow.to_pandas()

athletes = athletes[athletes['Category'] != "Qualification"]
athletes = athletes[athletes['Discipline'].isin(['Parallel Slalom', 'Slalom', 'Parallel GS', 'Parallel Giant Slalom', 'Giant Slalom'])]
athletes['FIS Points'] = pd.to_numeric(athletes['FIS Points'], downcast='integer', errors='coerce')


athletes['Date Formated'] = athletes.apply(lambda x: datetime.strptime(x['Date'],"%d-%m-%Y"), axis=1)
athletes = athletes.drop_duplicates().sort_values(by='Date Formated', ascending=True)

arrowFrame = pa.Table.from_pandas(athletes)
pq.write_table(arrowFrame, "AthletesCSV/formated.parquet", compression=None)

weather = pd.DataFrame()
weatherFiles = glob.glob(os.path.join("WeatherCSV", "*.csv")) 
  
# loop over the list of csv files 
for file in weatherFiles: 
    w = pd.read_csv(file)
    weather = pd.concat([w, weather])

# Merging weather data with results
weather['Date Formated'] = weather.apply(lambda x: datetime.strptime(x['Date'],"%Y-%m-%d"), axis=1)
weather['Temp Avg'] = weather['Temp Avg'].astype(float)

mergedAthletes = pd.merge(athletes, weather[['Location', 'Discipline', 'Date Formated', 'Temp Avg', 'Wind Speed']], on=['Location', 'Date Formated'], how="inner")

arrowMerged = pa.Table.from_pandas(mergedAthletes)
pq.write_table(arrowMerged, "AthletesCSV/merged.parquet", compression=None)


# Creating a dataframe for current points of single athletes
def currentPoints():
    todayDate = datetime.now()
    yearBack = todayDate.replace(year = todayDate.year - 1)

    allAthletes = athletes[(athletes['Date Formated'] >= yearBack) & (athletes['Date Formated'] <= todayDate)]
    allAthletes = allAthletes.dropna(subset=['FIS Points'])

    pointsFrame = pd.DataFrame(columns=['Name', 'Gender', 'Points', 'Nation', 'FIS', 'EC', 'WC'])

    # Counting the current FIS Points
    for name in allAthletes['Name'].unique():
        singleAthlete = allAthletes[(allAthletes['Name'] == name)]

        singleAthlete = singleAthlete.sort_values(by='FIS Points', ascending=False)
        points = singleAthlete['FIS Points'].tolist()
        
        if len(points) > 1:
            hisCurrent = (points[0] + points[1]) / 2

            # Seeing appearences in each category
            fisAppeared = len(singleAthlete[(singleAthlete['Category'] != 'World Cup') & (singleAthlete['Category'] != 'European Cup')])
            ecAppeared = len(singleAthlete[(singleAthlete['Category'] == 'European Cup')])
            wcAppeared = len(singleAthlete[(singleAthlete['Category'] == 'World Cup')])

            new = {'Name': name, 'Points': hisCurrent, 'Gender': singleAthlete['Gender'].unique()[0], 'Nation': singleAthlete['Nation'].unique()[0], 'FIS': fisAppeared, 'EC': ecAppeared, 'WC': wcAppeared} 
            newFrame = pd.DataFrame([new])
            pointsFrame = pd.concat([pointsFrame, newFrame])

    pointsFrame = pointsFrame.sort_values(by='Points', ascending=False)
    return pointsFrame

current = currentPoints()
arrowPoints = pa.Table.from_pandas(current)
pq.write_table(arrowPoints, "AthletesCSV/points.parquet", compression=None)