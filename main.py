from dash import Dash, dcc, html, Input, Output, callback, State, dash_table, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import os
import numpy as np
import random
from datetime import datetime

weather = pd.read_csv('Weather2023.csv')

filesCSV = [f for f in os.listdir('AthletesCSV') if f.endswith('.csv')]
dfs = []

for csv in filesCSV:
    df = pd.read_csv(os.path.join("AthletesCSV", csv))
    dfs.append(df)
    
athletes = pd.concat(dfs, ignore_index=True)
athletes = athletes[athletes['Category'] != "Qualification"]
athletes = athletes[athletes['Discipline'].isin(['Parallel Slalom', 'Slalom', 'Parallel GS', 'Parallel Giant Slalom', 'Giant Slalom'])]

athletes['Date Formated'] = athletes.apply(lambda x: datetime.strptime(x['Date'],"%d-%m-%Y"), axis=1)
athletes = athletes.drop_duplicates()

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll',
        'color': 'white',
    }
}

a = pd.merge(athletes, weather[['Location', 'Discipline', 'Date', 'Temp Avg', 'Wind Speed']], on=['Location', 'Date'], how="inner")
print(a)

# Creating a dataframe for current points of single athletes
def currentPoints(category, gender):
    allAthletes = athletes[athletes['Gender'] == gender]

    todayDate = datetime.now()
    yearBack = todayDate.replace(year = todayDate.year - 1)

    allAthletes = allAthletes[(allAthletes['Date Formated'] >= yearBack) & (allAthletes['Date Formated'] <= todayDate)]
    allAthletes =allAthletes.dropna(subset=['FIS Points'])

    pointsFrame = pd.DataFrame(columns=['Name', 'Points', 'Nation'])
    # Counting the current FIS Points
    for name in allAthletes['Name'].unique():
        singleAthlete = allAthletes[(allAthletes['Name'] == name)]

        # Seeing how many races of the single category this racer did in last year
        isActive = 1
        if category != None:
            controledFrame = singleAthlete[singleAthlete['Category'] == category]

            frameSize = len(controledFrame)

            if frameSize <= 1 and (category == 'FIS' or category == 'European Cup'):
                isActive = 0 
            elif frameSize <= 0 and category == 'World Cup':
                isActive = 0 

        if len(singleAthlete) >= 2 and isActive == 1:
            singleAthlete = singleAthlete.sort_values(by='FIS Points', ascending=False)
            points = singleAthlete['FIS Points'].tolist()
            hisCurrent = (points[0] + points[1]) / 2

            new = {'Name': name, 'Points': hisCurrent, 'Nation': singleAthlete['Nation'].unique()[0]} 
            newFrame = pd.DataFrame([new])
            pointsFrame = pd.concat([pointsFrame, newFrame])

    return pointsFrame

def bubbleChartPrep(ridersAmount, category, gender):
    currentPointsFrame = currentPoints(category, gender)

    nationsBubble = pd.DataFrame(columns=['X', 'Y', 'Points', 'Nation'])
    allHeadAthletes = pd.DataFrame() 

    for nation in currentPointsFrame['Nation'].unique():
        singleNation = currentPointsFrame[currentPointsFrame['Nation'] == nation].sort_values(by='Points', ascending=False)

        headRidersFull = singleNation.head(ridersAmount)
        headRiders = headRidersFull['Points']
        points = headRiders.tolist()

        x = random.randint(0, 99)
        y = random.randint(0, 99)
        average = sum(points) / ridersAmount
        new = {'X': x, 'Y': y, 'Points': average, 'Nation': nation} 
        newFrame = pd.DataFrame([new])
        nationsBubble = pd.concat([nationsBubble, newFrame])
        allHeadAthletes = pd.concat([allHeadAthletes, headRidersFull])

    if len(nationsBubble) > 0:
        nationsBubble['Points'] = nationsBubble['Points'].round(2)
        allHeadAthletes['Points'] = allHeadAthletes['Points'].round(2)

    return nationsBubble, allHeadAthletes

bubblePrep = bubbleChartPrep(5, None, 'Male')
lastCategory = None
lastGender = 'Male'

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

app.layout = dbc.Container([
    html.Div([
        html.Div([
            html.Div([
                html.H1([
                html.Span("Welcome"),
                html.Br(),
                html.Span("to an Athlete dashboard!")
            ]),

            html.Div([
                html.H5('Career best:'),
                html.Pre(id='click-best', style=styles['pre'])
            ], style={'display':'inline-block', 'width' : '100%', 'z-index': -1, 'position':'relative'}),

            html.Div([
                    html.H5('Average Points:'),
                    html.H6('(From clicked date)'),
                    html.Pre(id='click-average', style=styles['pre'])
            ], style={'display':'inline-block', 'width' : '100%'}),
        ], style={"vertical-alignment": "top"}),], id='introduction'),

        html.Div([
            html.Div([
                    dash_table.DataTable(
                        id='counted-athletes',
                        fill_width=False,
                    ),
                ], style={'display':'inline-block', 'width' : '100%', 'margin-top': 10, 'margin-bottom': 20}),

            html.Div([
                    html.H5('Nation Points:'),
                    html.Pre(id='points-bubble', style=styles['pre'])
                ], style={'display':'inline-block', 'width' : '100%'}),

            html.Div([
                    html.H5('Ranking:'),
                    html.Pre(id='rank-bubble', style=styles['pre'])
                ], style={'display':'inline-block', 'width' : '100%'}),
        ], id='counted-athletes-div'),

        html.Div(dbc.RadioItems(
                    id='layout-buttons',
                    className='btn-group',
                    inputClassName='btn-check',
                    labelClassName="btn btn-outline-light",
                    labelCheckedClassName="btn btn-light",
                    options=[
                        {"label": "SingleAthlete", "value": 1}, 
                        {"label": "Table", "value": 2}
                    ],
                    value=1
                ), style={'width': 206, 'display':'flex', 'margin-top':15}),

        html.Div([             
                html.Div(
                    [
                    dcc.Dropdown(
                        athletes['Nation'].unique(),
                        'Czechia',
                        multi=True,
                        className='customDropdown',
                        id='nation-dropbox'
                    )
                ], style={'margin-top': 15, 'margin-bottom': 15}),
                
                dcc.Dropdown(
                    athletes['Name'].unique(),
                    'Tulach Jaroslav',
                    id='name-dropbox',
                    className='customDropdown' 
                ),
                
                html.Div(
                    [
                    dcc.Slider(0, 10,
                        id='discipline-slider',
                        step=None,
                        marks={
                            0: 'SL',
                            5: 'ALL',
                            10: 'GS'
                        },
                        value=5
                    )
                ], style={'margin-top': 15, 'margin-bottom': 15}),
                
                html.Div(
                    [
                    dcc.Dropdown(
                    id='category-dropbox',
                    multi=True,
                    className='customDropdown' 
                    ),
                    
                ],style={'margin-top': 15, 'margin-bottom': 15}),
                
                dcc.Dropdown(
                    id='location-dropbox',
                    className='customDropdown'
                    ),
        ], id='filtration-single'),

        html.Div([             
                html.Div(
                    [
                    dcc.Dropdown(
                        athletes['Nation'].unique(),
                        'Germany',
                        className='customDropdown',
                        id='nationBubble'
                    )
                ], style={'margin-top': 15, 'margin-bottom': 15}),

                html.Div(
                    [
                    dcc.Dropdown(
                        ['Male', 'Female'],
                        'Male',
                        id='genderBubble',
                        className='customDropdown' 
                    ),
                ], style={'margin-top': 15, 'margin-bottom': 15}),

                html.Div(
                    [
                    dcc.Dropdown(
                        ['FIS', 'European Cup', 'World Cup'],
                        id='categoryBubble',
                        className='customDropdown'
                    ),
                ], style={'margin-top': 15, 'margin-bottom': 15}),
            ], id='filtration-nation'),
            
        ], style={'width': 340, 'margin-left': 35, 'margin-top': 35,'margin-bottom': 35}),
    

        html.Div([
            html.Div([
                dcc.Graph(id='athlete-chart'),
                dcc.Graph(id='nation-chart'),
            ], style={'width': 990, 'margin-top': 55, 'margin-right': 5, 'margin-bottom': 35, 'margin-left': 10,}),

        html.Div(className='roww', children=[
                    html.Div([
                        html.H5('Location:'),
                        html.Pre(id='click-location', style=styles['pre'])
                    ], style={'display':'inline-block', 'width' : '100%'}),

                    html.Div([
                        html.H5('Category:'),
                        html.Pre(id='click-category', style=styles['pre'])
                    ], style={'display':'inline-block', 'width' : '100%'}),

                    html.Div([
                        html.H5('National best:'),
                        html.Pre(id='click-nationbest', style=styles['pre'])
                    ], style={'display':'inline-block', 'width' : '100%'}),

                    html.Div([
                        html.H5('Position:'),
                        html.Pre(id='click-position', style=styles['pre'])
                    ], style={'display':'inline-block', 'width' : '100%'}),
            ], id='info-athlete')
        ], style={'display':'inline-block'}),

        dcc.Store(id="bubble-save-graph"),
        dcc.Store(id="bubble-save-table"),
        
], fluid=True, style={'display': 'flex'}, className='dashboard-container')

@callback(
    Output('athlete-chart', 'figure'),
    Output('click-location', 'children'),
    Output('click-position', 'children'),
    Output('click-best', 'children'),
    Output('click-average', 'children'),
    Output('click-category', 'children'),
    Output('click-nationbest', 'children'),
    Input('name-dropbox', 'value'),
    Input('location-dropbox', 'value'),
    Input('discipline-slider', 'value'),
    Input('category-dropbox', 'value'),
    Input('athlete-chart', 'clickData'),
    )
def singleAthlete(selectedName, location, selectedDiscipline, categoryList, click):
    # Filtering DataFrame by selected values in navigation bar
    personData = athletes[athletes['Name'] == selectedName]
    if selectedDiscipline == 0:
        slNames = ['Parallel Slalom', 'Slalom']
        personData = personData[personData['Discipline'].isin(slNames)]
    if selectedDiscipline == 10:
        gsNames = ['Parallel GS', 'Parallel Giant Slalom', 'Giant Slalom']
        personData = personData[personData['Discipline'].isin(gsNames)]
    if personData[personData['Location'] == location].empty != True:
        personData = personData[personData['Location'] == location]
       
    if categoryList == None:
        categoryList = []
    if categoryList != []:
        personData = personData[personData['Category'].isin(categoryList)]

    # Data for information bar under the graph
    locationClicked = None
    positionClicked = None
    maxPoints = None
    averageClicked = None
    categoryClicked = None
    nationBest = None

    if click != None:
        clickedDate = click['points'][0]['x']

        dateRow = personData[personData['Date'] == clickedDate]
        locationClicked = dateRow['Location']
        positionClicked = dateRow['Position']
        categoryClicked = dateRow['Category']

        averagetable = personData[personData['Date Formated'] >= datetime.strptime(clickedDate,"%d-%m-%Y")]
        averageClicked = averagetable['FIS Points'].mean()
    
    # Creating a chart
    fig = px.line()
    
    if selectedName != None and personData.empty != True:
        # Declaring information bar Non-clicked values
        maxPoints = personData.max()['FIS Points']
        if averageClicked == None:
            averageClicked = personData['FIS Points'].mean()

        fig = px.line(personData, x=personData['Date'], y=personData['FIS Points'], markers=True, color="Name")
        
        # Adding a line representing maximum performance for his nation on his race days
        if len(personData['Nation'].unique()) > 0:
            hisNation = athletes[athletes['Nation'] == personData['Nation'].unique()[0]]
            hisNation = hisNation[hisNation['Gender'] == personData['Gender'].unique()[0]]
            maximumNation = pd.DataFrame(columns=athletes.columns)
            for date in personData['Date'].unique():
                nationDayFrame = hisNation[hisNation['Date'] == date]
                maxIndex = nationDayFrame.nlargest(1, ['FIS Points'])
                maximumNation = pd.concat([maximumNation, maxIndex])
            fig.add_trace(go.Line(x=maximumNation['Date'], y=maximumNation['FIS Points'], name='National Best'))

            # Displaying the best racer of the day
            if click != None:
                nationBest = maximumNation[maximumNation['Date'] == clickedDate]['Name']

    # Updating Graph Design
    fig.update_layout(xaxis_title="Date", yaxis_title="FIS Points", plot_bgcolor='white', paper_bgcolor='#070635', width=960, height=500, font_color="white", margin=dict(l=0, r=0, t=0, b=0), hovermode='x unified', showlegend=False)
    fig.update_xaxes(gridcolor='lightgrey')
    fig.update_yaxes(gridcolor='lightgrey')
    fig.update_traces(mode="markers+lines", hovertemplate=None)
    
    return [fig, locationClicked, positionClicked, maxPoints, averageClicked, categoryClicked, nationBest]

@callback(
    Output('nationBubble', 'value'),
    Input('nation-chart', 'clickData'),
    State('nationBubble', 'value'),)
def nationFromGraph(click, currentNation):
    clickedNation = None
    if click != None:
        clickedNation = click['points'][0]['hovertext']
        return clickedNation
    return currentNation

@callback(
    [Output('nation-chart', 'figure'),
    Output('counted-athletes', 'data'),
    Output('counted-athletes', 'columns'),
    Output('points-bubble', 'children'),
    Output('rank-bubble', 'children'),
    Output('nationBubble', 'options'),
    Output('bubble-save-graph', 'data'),
    Output('bubble-save-table', 'data')],
    Input('nationBubble', 'value'),
    Input('genderBubble', 'value'),
    Input('categoryBubble', 'value'),
    Input('bubble-save-graph', 'data'),
    Input('bubble-save-table', 'data'))
def multipleNations(selectedNation, selectedGender, selectedCategory, graphStore, tableStore):
    # Configuring data passed into the bubble chart
    if ctx.triggered_id != 'nationBubble' or graphStore == None:
        bubblePrep = bubbleChartPrep(5, selectedCategory, selectedGender)

        nationsBubble = bubblePrep[0].sort_values(by='Points', ascending=False)
        nationsBubble.reset_index(inplace=True)
        acountedRiders = bubblePrep[1]
        print(nationsBubble)
    else:
        nationsBubble = pd.DataFrame(graphStore["data-frame"])
        acountedRiders = pd.DataFrame(tableStore["data-frame"])

    nationRank = None
    nationPoints = None
    data = None
    columns = None

    # Calculating information about the nation
    if selectedNation != None:
        nationFrame = nationsBubble[nationsBubble['Nation'] == selectedNation]
        if not nationFrame.empty:
            nationPoints = nationFrame['Points'].unique()[0]

            clickedAthletes = acountedRiders[acountedRiders['Nation'] == selectedNation]
            data=clickedAthletes.to_dict('records')
            columns=[{"name": i, "id": i} for i in clickedAthletes.columns]

            nationRank = nationFrame.index + 1

    fig = px.scatter(nationsBubble, x="X", y="Y",
	         size="Points", color="Nation", 
                 hover_name="Nation", log_x=True, size_max=60)

    # Updating Graph Design
    fig.update_layout(plot_bgcolor='#070635', paper_bgcolor='#070635', width=960, height=500, font_color="white", margin=dict(l=0, r=0, t=0, b=0))
    fig.update_xaxes(visible=False, showticklabels=False, gridcolor='lightgrey')
    fig.update_yaxes(visible=False, showticklabels=False, gridcolor='lightgrey')

    return fig, data, columns, nationPoints, nationRank, nationsBubble['Nation'].unique(), {"data-frame": nationsBubble.to_dict("records")}, {"data-frame": acountedRiders.to_dict("records")}

# Managing the dropdown options and overall callbacks of the navigation bar
@callback(
    Output('name-dropbox', 'options'),
    Input('nation-dropbox', 'value'))
def nameDrop(selectedNations):
    if type(selectedNations) != list:
        selectedNations = [selectedNations]
    b = pd.DataFrame()
    if selectedNations != None:
        for nation in selectedNations:
            b = pd.concat([b, athletes[athletes['Nation'] == nation]])
    if b.empty:
        b = athletes
    return b['Name'].unique()

@callback(
    Output('category-dropbox', 'options'),
    Input('name-dropbox', 'value'))
def categoryDrop(selectedName):
    if type(selectedName) != list:
        selectedName = [selectedName]
    b = pd.DataFrame()
    if selectedName != None:
        for name in selectedName:
            b = pd.concat([b, athletes[athletes['Name'] == name]])
    if b.empty:
        b = athletes
        
    return b['Category'].unique()

@callback(
    Output('location-dropbox', 'options'),
    Input('name-dropbox', 'value'),
    Input('category-dropbox', 'value'))
def locationDrop(selectedName, categoryList):
    b = pd.DataFrame()
    if selectedName != None:
        b = athletes[athletes['Name'] == selectedName]
        
    if categoryList == None:
        categoryList = []
    if categoryList != []:
        b = b[b['Category'].isin(categoryList)]
        
    if b.empty:
        b = athletes
    return b['Location'].unique()

@callback(
   [Output('athlete-chart', 'style'),
   Output('nation-chart', 'style'),
   Output('introduction', 'style'),
   Output('counted-athletes-div', 'style'),
   Output('filtration-single', 'style'),
   Output('filtration-nation', 'style'),
   Output('info-athlete', 'style')],
   Input('layout-buttons', 'value')
)
def switchVisibility(content):
   if content == 2:
       return {'display':'none'},  {'display':'inline'}, {'display':'none'}, {'margin-top':20}, {'display':'none'}, {'display':'inline'}, {'display':'none'}
   else:
       return {'display':'inline'},  {'display':'none'}, {'display':'inline'}, {'display':'none'}, {'display':'inline'}, {'display':'none'}, {'width': 970, 'margin-left': 35, 'margin-top': 5, 'margin-right': 35, 'margin-bottom': 35, 'display': 'flex', 'height':100}
   
       
if __name__ == '__main__':
    app.run(debug=True)
    