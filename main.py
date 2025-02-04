from dash import Dash, dcc, html, Input, Output, callback, State, dash_table, ctx, dash
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

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll',
        'color': 'white',
    }
}

arrowAthletes = pq.read_table("AthletesCSV/formated.parquet")
athletes = arrowAthletes.to_pandas()

arrowMerged = pq.read_table("AthletesCSV/merged.parquet")
mergedAthletes = arrowMerged.to_pandas()

arrowPoints = pq.read_table("AthletesCSV/points.parquet")
pointsFrame = arrowPoints.to_pandas()

# Creating a dataframe for current points of single athletes
def currentPoints(category, gender):
    allAthletes = pointsFrame[pointsFrame['Gender'] == gender]

    if category != None:
        if category == 'FIS':
            allAthletes = allAthletes[(allAthletes['FIS'] > 1)]
        if category == 'European Cup':
            allAthletes = allAthletes[(allAthletes['European Cup'] > 1)]
        if category == 'World Cup':
            allAthletes = allAthletes[(allAthletes['World Cup'] > 0)]

    return allAthletes

def weatherPrep(name):
    weatherFrame = mergedAthletes[mergedAthletes['Name'] == name]
    print(weatherFrame)
    underZero = weatherFrame[weatherFrame['Temp Avg'] <= 0]
    aboveZero = weatherFrame[weatherFrame['Temp Avg'] > 0]

    averageUnder = underZero['FIS Points'].mean()
    averageOver = aboveZero['FIS Points'].mean()
    return averageUnder, averageOver

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
        nationsBubble = pd.concat([nationsBubble, newFrame], ignore_index=True)
        allHeadAthletes = pd.concat([allHeadAthletes, headRidersFull])

    if len(nationsBubble) > 0:
        nationsBubble['Points'] = nationsBubble['Points'].round(2)
        allHeadAthletes['Points'] = allHeadAthletes['Points'].round(2)

    return nationsBubble, allHeadAthletes

bubblePrep = bubbleChartPrep(5, None, 'Male')
lastCategory = None
lastGender = 'Male'

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY, '/assets/responsive_updated.css'])
server = app.server

app.layout = dbc.Container([
    html.Div([
        html.Div([ 
            html.Div([
                html.H1([
                html.Span("Welcome"),
                html.Br(),
                html.Span("to a snowboarding dashboard!")
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
                        style_cell={
                            'height': 'auto',
                            # all three widths are needed
                            'minWidth': 155, 'width': 155, 'maxWidth': 155,
                            'whiteSpace': 'normal',
                            'border': '1px solid white'
                        },
                        style_data={
                            'color': 'white',
                            'backgroundColor': '#070635'
                        },
                        style_header={'color': 'white', 'border': '1px solid white', 'backgroundColor': '#15152b'},
                    ),
                ], style={'height': 210,'display':'inline-block', 'width' : '100%', 'margin-top': 5, 'margin-bottom': 20}),

            html.Div([
                    html.H5('Nation Points:'),
                    html.Pre(id='points-bubble', style=styles['pre'])
                ], style={'display':'inline-block', 'width' : '100%'}),

            html.Div([
                    html.H5('Ranking:'),
                    html.Pre(id='rank-bubble', style=styles['pre'])
                ], style={'display':'inline-block', 'width' : '100%'}),
        ], id='counted-athletes-div'),

        html.Div([
            html.Div(dbc.RadioItems(
                        id='layout-buttons',
                        className='btn-group',
                        inputClassName='btn-check',
                        labelClassName="btn btn-outline-light",
                        labelCheckedClassName="btn btn-light",
                        options=[
                            {"label": "SingleAthlete", "value": 1}, 
                            {"label": "Calculator", "value": 2}
                        ],
                        value=1
            ), style={'width': 206}),
            html.Div(dbc.Button(
                "Manual",
                className="btn btn-info",
                n_clicks=1,
                id='manual-button'
            ), style={'width': 104}),
        ], style={'display': 'flex', 'margin-top':15}),

        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("HOW TO USE THIS APP?", style={'text-align': 'center', 'color': '#007bff'})),
                html.Div([
                    dbc.ModalBody([
                        html.Div("Follow these steps to navigate the FIRST PART dashboard, offering fast data analysis:", style={'font-weight': 'bold', 'margin-bottom': '10px'}),
                        html.Div("Step 1:", style={'color': '#007bff'}),
                        html.Div([
                            html.Div(["Choose athlete's NAME in the control panel, which you can also filter by NATION"], style={'font-size':19, 'margin-bottom': 7}),
                            html.Button("↵", id='picture1button', n_clicks=0, className='imgbutton o'),
                        ], style={'display': 'flex'}),
                        html.Div([
                            html.Img(src='assets/first.png', style={'width': '60%', 'height': 'auto'}),
                        ], id='picture1', style={'display':'none'}),

                        html.Div("Step 2:", style={'color': '#007bff'}),
                        html.Div([
                            html.Div(["Select specifications for the showed data, such as DISCIPLINE, CATEGORY and LOCATION"], style={'font-size':19, 'margin-bottom': 7}),
                            html.Button("↵", id='picture2button', n_clicks=0, className='imgbutton o'),
                        ], style={'display': 'flex'}),
                        html.Div([
                            html.Img(src='assets/second.png', style={'width': '60%', 'height': 'auto'}),
                        ], id='picture2', style={'display':'none'}),

                        html.Div("Step 3:", style={'color': '#007bff'}),
                        html.Div([
                            html.Div(["Watch race data in graph, where:"], style={'font-size':19, 'margin-bottom': 5}),
                            html.Button("↵", id='picture3button', n_clicks=0, className='imgbutton o'),
                        ], style={'display': 'flex'}),
                        html.Div([
                            html.Img(src='assets/third.png', style={'width': '60%', 'height': 'auto'}),
                        ], id='picture3', style={'display':'none'}),
                        html.Ul([
                            html.Li(["Purple = Athletes performance"]),
                            html.Li(["Green = Best performance achieved by his Nation"]),
                            html.Li(["Blue = Average performance in temperatures < 0°C"]),
                            html.Li(["Red = Average performance in temperatures > 0°C"]),
                        ]),

                        html.Div("Step 4:", style={'color': '#007bff'}),
                        html.Div([
                            html.Div(["Click on the graph to display more details in information panel"], style={'font-size':19, 'margin-bottom': 5}),
                            html.Button("↵", id='picture4button', n_clicks=0, className='imgbutton o'),
                        ], style={'display': 'flex'}),
                        html.Div([
                            html.Img(src='assets/fourth.png', style={'width': '60%', 'height': 'auto'}),
                        ], id='picture4', style={'display':'none'}),
                    ]),
                ], id='firstPage'),

                html.Div([
                    dbc.ModalBody([
                        html.Div("Follow these steps to navigate the SECOND PART dashboard, offering fast data analysis:", style={'font-weight': 'bold', 'margin-bottom': '10px'}),
                        html.Div("Step 1:", style={'color': '#007bff'}),
                        html.Div([
                            html.Div(["Select NATION by either using the control panel or clicking on bubble in graph"], style={'font-size':19, 'margin-bottom': 7}),
                            html.Button("↵", id='2picture1button', n_clicks=0, className='imgbutton o'),
                        ], style={'display': 'flex'}),
                        html.Div([
                            html.Img(src='assets/firstBubble.png', style={'width': '60%', 'height': 'auto'}),
                        ], id='2picture1', style={'display':'none'}),

                        html.Div("Step 2:", style={'color': '#007bff'}),
                        html.Div([
                            html.Div(["Select specifications for used data, such as GENDER and RACE TYPE"], style={'font-size':19, 'margin-bottom': 7}),
                            html.Button("↵", id='2picture2button', n_clicks=0, className='imgbutton o'),
                        ], style={'display': 'flex'}),
                        html.Div(["RACE TYPE - Includes only active athletes for selected race type"], style={'font-size':14, 'margin-bottom': 7}),
                        html.Div([
                            html.Img(src='assets/secondBubble.png', style={'width': '60%', 'height': 'auto'}),
                        ], id='2picture2', style={'display':'none'}),

                        html.Div("Step 3:", style={'color': '#007bff'}),
                        html.Div([
                            html.Div(["Analyse the information panel and Athletes table"], style={'font-size':19, 'margin-bottom': 5}),
                            html.Button("↵", id='2picture3button', n_clicks=0, className='imgbutton o'),
                        ], style={'display': 'flex'}),
                        html.Div(["Athletes table - Displays accounted athletes"], style={'font-size':14, 'margin-bottom': 5}),
                        html.Div([
                            html.Img(src='assets/thirdBubble.png', style={'width': '60%', 'height': 'auto'}),
                        ], id='2picture3', style={'display':'none'}),
                        ],)
                ], id='secondPage'),
            ],
            id="manual",
            size="xl",
            is_open=False,
        ),

        html.Div([             
                html.Div(
                    [
                    dcc.Dropdown(
                        athletes['Nation'].unique(),
                        'Czechia',
                        multi=True,
                        className='customDropdown',
                        id='nation-dropbox',
                        placeholder="Nation..."
                    )
                ], style={'margin-top': 15, 'margin-bottom': 15}),
                
                dcc.Dropdown(
                    athletes['Name'].unique(),
                    'Tulach Jaroslav',
                    id='name-dropbox',
                    className='customDropdown' ,
                    placeholder="Name..."
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
                    className='customDropdown',
                    placeholder="Category..."
                    ),
                    
                ],style={'margin-top': 15, 'margin-bottom': 15}),
                
                dcc.Dropdown(
                    id='location-dropbox',
                    className='customDropdown',
                    placeholder="Location.."
                    ),
        ], id='filtration-single'),

        html.Div([             
                html.Div(
                    [
                    dcc.Dropdown(
                        athletes['Nation'].unique(),
                        'Germany',
                        className='customDropdown',
                        id='nationBubble',
                        placeholder="Nation..."
                    )
                ], style={'margin-top': 15, 'margin-bottom': 15}),

                html.Div(
                    [
                    dcc.Dropdown(
                        ['Male', 'Female'],
                        'Male',
                        id='genderBubble',
                        className='customDropdown',
                        placeholder="Gender..."
                    ),
                ], style={'margin-top': 15, 'margin-bottom': 15}),

                html.Div(
                    [
                    dcc.Dropdown(
                        ['FIS', 'European Cup', 'World Cup'],
                        id='categoryBubble',
                        className='customDropdown',
                        placeholder="Category..."
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
                html.H5('Position:'),
                html.Pre(id='click-position', style=styles['pre'])
            ], style={'display':'inline-block', 'width' : '100%'}),

            html.Div([
                html.H5('National best:'),
                html.Pre(id='click-nationbest', style=styles['pre'])
            ], style={'display':'inline-block', 'width' : '100%'}),
        ], id='info-athlete'),

        html.Div(className='roww', children=[
            html.Div([
                html.H5('Average Under:'),
                html.Pre(id='click-under', style=styles['pre'])
            ], style={'display':'inline-block', 'width' : '100%'}),
            
            html.Div([
                html.H5('Average Over:'),
                html.Pre(id='click-over', style=styles['pre'])
            ], style={'display':'inline-block', 'width' : '100%'}),
        ], id='info-bubble')
        ], style={'display':'inline-block'}),

        dcc.Store(id="bubble-save-graph"),
        dcc.Store(id="bubble-save-table"),
        
], fluid=True, style={'display': 'flex'}, className='dashboard-container')

@callback( 
    Output("manual", "is_open"), 
    Input("manual-button", "n_clicks"), 
    State("manual", "is_open"), 
) 
def manualOpening(but, openIt): 
    if but: 
        return not openIt 
    return openIt 

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
    personData = personData.drop_duplicates(subset=['Date'])

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
        # Adding a line representing maximum performance for his nation on his race days
        if len(personData['Nation'].unique()) > 0:
            hisNation = athletes[athletes['Nation'] == personData['Nation'].unique()[0]]
            hisNation = hisNation[hisNation['Gender'] == personData['Gender'].unique()[0]]
            maximumNation = pd.DataFrame(columns=athletes.columns)
            for date in personData['Date'].unique():
                nationDayFrame = hisNation[hisNation['Date'] == date]
                maxIndex = nationDayFrame.nlargest(1, ['FIS Points'])
                maximumNation = pd.concat([maximumNation, maxIndex])
            if not maximumNation.empty:
                fig.add_trace(go.Line(x=maximumNation['Date'], y=maximumNation['FIS Points'], name='National Best', line=dict(color="green"), hoverinfo='text',
                hovertext="NB - " + maximumNation['Name'] + ': ' + maximumNation['FIS Points'].astype(str)))

            # Displaying the best racer of the day
            if click != None:
                nationBest = maximumNation[maximumNation['Date'] == clickedDate]['Name']

        # Declaring information bar Non-clicked values
        maxPoints = personData.max()['FIS Points']
        if averageClicked == None:
            averageClicked = personData['FIS Points'].mean()

        traceAthlete = go.Line(
            x=personData['Date'], 
            y=personData['FIS Points'], 
            name=selectedName, 
            line=dict(color='purple', width=3),
            hoverinfo='text',
            hovertext=personData['Name'] + ': ' + personData['FIS Points'].astype(str)
        )

        fig.add_trace(traceAthlete)

        # DECLARING AVERAGE WEATHER PERFORMANCE
        under, over = weatherPrep(selectedName)

        if over != None or under != None:
            tableWeather = pd.DataFrame()
            tableWeather['Date'] = personData['Date']
            tableWeather['Name'] = personData['Name']
            tableWeather['Over'] = over
            tableWeather['Under'] = under

            tableWeather = pd.concat([tableWeather.head(1), tableWeather.tail(1)])

        if over != None:
            fig.add_trace(go.Line(x=tableWeather['Date'], y=tableWeather['Over'], line=dict(color="#bd1816"), hoverinfo='text',
            hovertext='Over' + ': ' + str(over)))

        if under != None:
            fig.add_trace(go.Line(x=tableWeather['Date'], y=tableWeather['Under'], line=dict(color="#88c7dc"), hoverinfo='text',
            hovertext='Under' + ': ' + str(under)))
        
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
    Output('bubble-save-table', 'data'),
    Output('click-under', 'children'),
    Output('click-over', 'children'),],
    Input('nationBubble', 'value'),
    Input('genderBubble', 'value'),
    Input('categoryBubble', 'value'),
    State('bubble-save-graph', 'data'),
    State('bubble-save-table', 'data'))
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
            clickedAthletes[['Under', 'Over']] = clickedAthletes['Name'].apply(lambda x: weatherPrep(x)).apply(pd.Series)

            data=clickedAthletes[['Name', 'Points']].to_dict('records')
            columns=[{"name": i, "id": i} for i in clickedAthletes[['Name', 'Points']].columns]

            nationRank = nationFrame.index + 1

    fig = px.scatter(nationsBubble, x="X", y="Y",
                 size="Points", color="Nation", 
                 hover_name='Nation', hover_data={"Nation":False, "X": False, "Y": False, "Points": True}, log_x=True, size_max=60)

    # Updating Graph Design
    fig.update_layout(plot_bgcolor='#070635', paper_bgcolor='#070635', width=960, height=500, font_color="white", margin=dict(l=0, r=0, t=0, b=0))
    fig.update_xaxes(visible=False, showticklabels=False, gridcolor='lightgrey')
    fig.update_yaxes(visible=False, showticklabels=False, gridcolor='lightgrey')

    return fig, data, columns, nationPoints, nationRank, nationsBubble['Nation'].unique(), {"data-frame": nationsBubble.to_dict("records")}, {"data-frame": acountedRiders.to_dict("records")}, clickedAthletes['Under'].mean(), clickedAthletes['Over'].mean()

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
   Output('info-athlete', 'style'),
   Output('firstPage', 'style'),
   Output('secondPage', 'style'),
   Output('info-bubble', 'style'),],
   Input('layout-buttons', 'value')
)
def switchVisibility(content):
   if content == 2:
       return {'display':'none'},  {'display':'inline'}, {'display':'none'}, {'margin-top':20}, {'display':'none'}, {'display':'inline'}, {'display':'none'}, {'display':'none'}, {'display':'inline'}, {'width': 970, 'margin-left': 35, 'margin-top': 5, 'margin-right': 35, 'margin-bottom': 35, 'display': 'flex', 'height':100}
   else:
       return {'display':'inline'},  {'display':'none'}, {'display':'inline'}, {'display':'none'}, {'display':'inline'}, {'display':'none'}, {'width': 970, 'margin-left': 35, 'margin-top': 5, 'margin-right': 35, 'margin-bottom': 35, 'display': 'flex', 'height':100}, {'display':'inline'},  {'display':'none'},  {'display':'none'}
   
# Swapping visibility in manuals
@callback(
   Output('picture1', 'style'),
   Input('picture1button', 'n_clicks'),
   State('picture1', 'style')
)
def switchImg1(clicks, style):
   if clicks == 0:
       return {'display':'none'} 
   elif style == {'display':'inline', 'margin-bottom': 7}:
       return {'display':'none'} 
   else:
       return {'display':'inline', 'margin-bottom': 7}
   
@callback(
   Output('picture2', 'style'),
   Input('picture2button', 'n_clicks'),
   State('picture2', 'style')
)
def switchImg2(clicks, style):
   if clicks == 0:
       return {'display':'none'} 
   elif style == {'display':'inline', 'margin-bottom': 7}:
       return {'display':'none'} 
   else:
       return {'display':'inline', 'margin-bottom': 7}
   
@callback(
   Output('picture3', 'style'),
   Input('picture3button', 'n_clicks'),
   State('picture3', 'style')
)
def switchImg3(clicks, style):
   if clicks == 0:
       return {'display':'none'} 
   elif style == {'display':'inline', 'margin-bottom': 7}:
       return {'display':'none'} 
   else:
       return {'display':'inline', 'margin-bottom': 7}
   
@callback(
   Output('picture4', 'style'),
   Input('picture4button', 'n_clicks'),
   State('picture4', 'style')
)
def switchImg4(clicks, style):
   if clicks == 0:
       return {'display':'none'} 
   elif style == {'display':'inline', 'margin-bottom': 7}:
       return {'display':'none'} 
   else:
       return {'display':'inline', 'margin-bottom': 7}
   

@callback(
   Output('2picture1', 'style'),
   Input('2picture1button', 'n_clicks'),
   State('2picture1', 'style')
)
def secondPageSwitch1(clicks, style):
   if clicks == 0:
       return {'display':'none'} 
   elif style == {'display':'inline', 'margin-bottom': 7}:
       return {'display':'none'} 
   else:
       return {'display':'inline', 'margin-bottom': 7}
   
@callback(
   Output('2picture2', 'style'),
   Input('2picture2button', 'n_clicks'),
   State('2picture2', 'style')
)
def secondPageSwitch2(clicks, style):
   if clicks == 0:
       return {'display':'none'} 
   elif style == {'display':'inline', 'margin-bottom': 7}:
       return {'display':'none'} 
   else:
       return {'display':'inline', 'margin-bottom': 7}
   
@callback(
   Output('2picture3', 'style'),
   Input('2picture3button', 'n_clicks'),
   State('2picture3', 'style')
)
def secondPageSwitch3(clicks, style):
   if clicks == 0:
       return {'display':'none'} 
   elif style == {'display':'inline', 'margin-bottom': 7}:
       return {'display':'none'} 
   else:
       return {'display':'inline', 'margin-bottom': 7}
   
   if clicks == 0:
       return {'display':'none'} 
   elif style == {'display':'inline', 'margin-bottom': 7}:
       return {'display':'none'} 
   else:
       return {'display':'inline', 'margin-bottom': 7}
   
       
if __name__ == '__main__':
    app.run(debug=True)
    
