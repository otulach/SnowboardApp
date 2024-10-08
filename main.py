from dash import Dash, dcc, html, Input, Output, callback
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

app = Dash()

app.layout = [
    dcc.Dropdown(
                athletes['Name'].unique(),
                'Minarik Krystof',
                id='xaxis-column'
            ),
    dcc.Graph(id='indicator-graphic')
]

@callback(
    Output('indicator-graphic', 'figure'),
    Input('xaxis-column', 'value'))
def update_graph(xaxis_column_name):
    personData = athletes[(athletes['Name'] == xaxis_column_name) & (athletes['Category'] != "Qualification")]
    
    fig = px.line(x=personData['Date'],
                    y=personData['FIS Points'],
                    markers=True)

    fig.update_layout(
                    title="Athletes Data",
                    xaxis_title="Date",
                    yaxis_title="FIS Points")

    return fig

if __name__ == '__main__':
    app.run(debug=True)