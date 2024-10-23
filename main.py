from dash import Dash, dcc, html, Input, Output, callback, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import os
import numpy as np


filesCSV = [f for f in os.listdir('AthletesCSV') if f.endswith('.csv')]
dfs = []

for csv in filesCSV:
    df = pd.read_csv(os.path.join("AthletesCSV", csv))
    dfs.append(df)
    
athletes = pd.concat(dfs, ignore_index=True)
maximumPoints = None

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

app.layout = dbc.Container([
    html.Div([
        html.Div([
            html.H1([
                html.Span("Welcome"),
                html.Br(),
                html.Span("to an Athlete dashboardard!")
            ]),
            html.P("This app is designed to give you easy access to all the sports stats you need. Whether you want to follow your nation, check on how athletes are performing, or keep up with race results, you can do it all from one simple dashboard. No more searching around! Everything is organized and easy to find, so you can quickly get the stats you're looking for. Our dashboard makes following sports easier and more enjoyable!")
            ],
            style={
                "vertical-alignment": "top",
                "height": 410
            }),
        
            html.Div(
            [
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
                ), style={'width': 206,
                          'display':'flex'}),
            ]),
            
            dcc.Dropdown(
            id='name-dropbox',
            className='customDropdown' 
            ),
            dcc.Dropdown(
                athletes['Nation'].unique(),
                'Czechia',
                multi=True,
                className='customDropdown',
                id='nation-dropbox'
            ),
        ],
             style={
        'width': 340,
        'margin-left': 35,
        'margin-top': 35,
        'margin-bottom': 35
        }
        ),
    html.Div([
        dcc.Graph(id='athlete-chart'),
        dcc.Graph(id='nation-chart')
    ],
        style={
            'width': 990,
            'margin-top': 35,
            'margin-right': 35,
            'margin-bottom': 35
        })
],
    fluid=True,
    style={'display': 'flex'},
    className='dashboard-container')


@callback(
    Output('athlete-chart', 'figure'),
    Input('name-dropbox', 'value'))
def singleAthlete(selectedName):
        
    personData = athletes[(athletes['Name'] == selectedName) & (athletes['Category'] != "Qualification")]
    fig = px.line()
    if selectedName != None:
        fig = px.line(x=personData['Date'],
                        y=personData['FIS Points'],
                        markers=True,
                        labels=dict(x="Date", y="FIS Points"))

    fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="FIS Points",
                    plot_bgcolor='white',
                    paper_bgcolor='#000a5f',
                    width=790,
                    height=500,
                    margin=dict(l=0, r=0, t=0, b=0),
                    font_color="white",)
    
    fig.update_xaxes(
    gridcolor='lightgrey'
    )
    
    fig.update_yaxes(
        gridcolor='lightgrey'
    )
    
    return fig
        
@callback(
    Output('nation-chart', 'figure'),
    Input('name-dropbox', 'value'),
    Input('nation-dropbox', 'value'))
def multipleNations(selectedName, selectedNations):
    if type(selectedNations) != list:
        selectedNations = [selectedNations]
    nationsFrame = pd.DataFrame(columns=['Date', 'FIS Points', 'Nation'])
    
    for nation in selectedNations:
        frameSingleNation = athletes[athletes['Nation'] == nation]
        frameSingleNation["FIS Points"] = pd.to_numeric(frameSingleNation["FIS Points"], errors="coerce")
        frameSingleNation.dropna(subset=["FIS Points"], inplace=True)
        
        uniqueDates = frameSingleNation['Date'].unique()
        if selectedName != None:
            uniqueDates = athletes[athletes['Name'] == selectedName]['Date'].unique()
            
        for date in uniqueDates:
            finishedThisDay = frameSingleNation[frameSingleNation['Date'] == date]
        
            nationsFrame = pd.concat([nationsFrame, pd.DataFrame.from_dict({'Date' : [date], 'FIS Points' : [finishedThisDay["FIS Points"].sum() / len(finishedThisDay)], 'Nation' : [nation]})])
  
    fig = px.line(nationsFrame, x='Date', y='FIS Points', color='Nation', markers=True)

    fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Average FIS Points",
                    paper_bgcolor='#000a5f',
                    width=960,
                    height=500,
                    margin=dict(l=0, r=0, t=0, b=0),
                    font_color="white",)
    
    fig.update_xaxes(
    gridcolor='lightgrey'
    )
    
    fig.update_yaxes(
        gridcolor='lightgrey'
    )

    return fig

@callback(
    Output('name-dropbox', 'options'),
    Input('nation-dropbox', 'value'))
def updateNameDropbox(selectedNations):
    if type(selectedNations) != list:
        selectedNations = [selectedNations]
    a = athletes
    b = pd.DataFrame()
    if selectedNations != None:
        for nation in selectedNations:
            b = pd.concat([b, a[a['Nation'] == nation]])
    if b.empty:
        b = a
    return b['Name'].unique()

@app.callback(
   [Output('athlete-chart', 'style'),
   Output('nation-chart', 'style')],
   Input('layout-buttons', 'value')
)
def update_style(content):
   if content == 2:
       return {'display':'none'},  {'display':'inline'}
   else:
       return {'display':'inline'},  {'display':'none'}
       


if __name__ == '__main__':
    app.run(debug=True)