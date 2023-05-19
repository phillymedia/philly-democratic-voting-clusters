##################################################
# IMPORTS
##################################################

## Constants
TITLE = 'Philadata'

## Sys imports
from datetime import datetime as dt
import os,sys,copy,time

## Non-sys imports
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from dash import Dash, dcc, html, Input, Output, dash_table
import pandas_dash
from functools import lru_cache


#############
# DATA SETUP #
#############

def load_precinct_data():
    df=pd.read_csv('prec_results_demos.csv')
    df['prec_20'] = df['prec_20'].apply(lambda x: f'{int(x):04}')
    df['ward'] = df['prec_20'].apply(lambda x: x[:2])
    df['prec'] = df['prec_20'].apply(lambda x: x[2:])
    return df.set_index(['ward','prec']).sort_index()

df = load_precinct_data()

#############
# APP SETUP #
#############

## Setup plotly
# Plotly mapbox public token
mapbox_access_token = open(os.path.expanduser('~/.mapbox_token')).read()
px.set_mapbox_access_token(mapbox_access_token)

# Setup app
app = Dash(
    __name__, 
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title=TITLE,
)
server = app.server


x_axis = dbc.Checklist(options=df.columns, value='edu_attain')
y_axis = dcc.Dropdown(options=df.columns, value='renter_rate')
z_axis = dcc.Dropdown(options=df.columns)

filter_card = dbc.Card([

    x_axis,
    y_axis,
    z_axis
])


leftcol = dbc.Col([
    html.Div(html.H1(TITLE), id='title-div'),

    filter_card
    
], width=4, id='layout-col-left')


graph = dcc.Graph(id='members-map', className='div-for-charts')

rightcol = dbc.Col([
    graph
], width=8, id='layout-col-right')



app.layout = dbc.Container(dbc.Row([leftcol, rightcol]), id='layout-container')



@app.callback(
    
    Output(graph, "figure"),
    [
        Input(x_axis, 'value'),
        Input(y_axis, 'value'),
        # Input('dropdown-nation', 'value'),
        # Input('dropdown-gender', 'value'),
    ]
)
def update_map_and_table(x_axis, y_axis):
    fig = px.scatter(
        df.reset_index(),
        x=x_axis,
        y=y_axis,
        template='plotly_dark',
        trendline="ols"
    )
    return fig

    












if __name__ == "__main__":
    app.run(
        host='0.0.0.0', 
        debug=True,
        port=8052,
        # threaded=True,
        # dev_tools_ui=Fas,
        use_reloader=True,
        use_debugger=True,
        reloader_interval=1,
        reloader_type='watchdog'
    )


