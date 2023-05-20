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
import dash_mantine_components as dmc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from dash import Dash, dcc, html, Input, Output, State, dash_table, callback, ctx
import pandas_dash
from functools import lru_cache

from app_toolbox import *
from philadata import *



#############
# APP SETUP #
#############

## Setup plotly
# Plotly mapbox public token
mapbox_access_token = open(os.path.expanduser('~/.mapbox_token')).read()
px.set_mapbox_access_token(mapbox_access_token)
px.defaults.template='plotly_dark'

# Setup app
app = Dash(
    __name__, 
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    # external_stylesheets=[dbc.themes.BOOTSTRAP],
    title=TITLE,
)
server = app.server


def get_select_cols(cols=None, id=None,value=None,input_type=dmc.Select,**kwargs):
    if cols is None: cols = get_nonelectoral_cols() + get_electoral_cols()
    return input_type(
        data=[dict(label=x.title().replace('_',' '), value=x) for x in cols],
        id=id,
        value=value,
        # searchable=True,
        # clearable=True,
        # nothingFound="No cols found",
        className='select',
        # style={"width": 200},
        # **kwargs
    )









#### LAYOUT ####




def get_x_axis_select():
    return get_select_cols(
        id='x-axis', 
        label='X-axis', 
        placeholder='Select column for X-axis', 
        value='edu_attain'
    )
def get_y_axis_select():
    return get_select_cols(
        id='y-axis',
        label='Y-axis',
        placeholder='Select column for Y-axis',
        value='PRESIDENT OF THE UNITED STATES-DEM_BERNIE SANDERS'
    )
    
def get_qual_col_select():
    return get_select_cols(
        cols=get_qual_cols(),
        id='qual-col',
        label='Color by',
        placeholder='Select column for color',
        value='largest_race'
    )


def get_parcoords():
    df=precinct_data()[get_nonelectoral_cols()]
    fig = px.parallel_coordinates(
        df,
    )
    return fig



app.layout = lambda: dmc.MantineProvider(
    theme={"colorScheme": "dark"},
    children=[
        dmc.Grid(
            children=[
                dmc.Col(
                    span=3,
                    className='layout-col-left',
                    children=[
                        dmc.Title(TITLE),
                        dmc.Container(get_qual_col_select(), id='qual-col-container'),
                        dmc.Container(get_y_axis_select(), id='y-axis-container'),
                        dmc.Container(get_x_axis_select(), id='x-axis-container'),
                    ]
                ),

                dmc.Col(
                    span=9,
                    children=[
                        dcc.Graph(id='biplot'),
                        dcc.Graph(id='parcoord', figure=get_parcoords()),
                    ]
                )
            ]
        ),

        ## hidden
        html.Div(id='etcx', style={'display':'none'}),
        dcc.Store(id='parcoord-data')
    ]
)




@callback(    
    Output('parcoord-data', "data"),
    Input('parcoord', 'restyleData'),
    State('parcoord-data', "data"),
)
def update_par_coord_graph(restyledata, data):
    print(data)
    return (data if data else []) + (restyledata if restyledata else [])


@callback(    
    Output('etcx', "children"),
    Input('parcoord-data', 'data'),
)
def f(x):
    print('!!!',x)







@callback(
    Output('x-axis-container', 'children'),
    [
        Input('y-axis','value'),
        State('x-axis','value')
    ]
)
def update_x_axis_options(y_axis, x_axis):
    qcols = list(get_nonelectoral_cols(quant=True))
    s = corr_data()[y_axis].loc[qcols].sort_values(ascending=False)
    options = [
        (f'({cor*100:.3}%) {get_label_str(x)}', x)
        for x,cor in zip(s.index, s)
        if cor != 1
        and not x+'_share' in set(s.index)
    ]
    return get_chip_group(
        options,
        label='X-axis options',
        multiple=False,
        id='x-axis',
        value=x_axis if x_axis else options[0][1],
        # position='center'
    )








@callback(    
    Output('biplot', "figure"),
    [
        Input('x-axis', 'value'),
        Input('y-axis', 'value'),
        Input('qual-col', 'value')
    ]
)
def update_map_and_table(x_axis, y_axis, qual_col):
    fig = px.scatter(
        fig_data(),
        x=x_axis,
        y=y_axis,
        color=qual_col,
        template='plotly_dark',
        # trendline="ols",
        # trendline_color_override="orange",
        # trendline_scope='overall',
        # trendline_options=dict(frac=0.1)
        marginal_x='box',
        marginal_y='box'
    )
    return fig

    









if __name__ == "__main__":
    print('running')
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


