##################################################
# IMPORTS
##################################################

## Constants
TITLE = 'Philadata'

## Sys imports
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime as dt
import os,sys,copy,time

## Non-sys imports
import dash
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from dash import Dash, dcc, html, Input, Output, State, dash_table, callback, ctx
import pandas_dash
from functools import lru_cache, cached_property

from app_toolbox import *
from philadata import *

from dash_oop_components import DashFigureFactory, DashComponent, DashComponentTabs, DashApp

## Setup plotly
# Plotly mapbox public token
mapbox_access_token = open(os.path.expanduser('~/.mapbox_token')).read()
px.set_mapbox_access_token(mapbox_access_token)
px.defaults.template='plotly_dark'


def is_l(x): return type(x) in {list,tuple}
def iter_minmaxs(l):
    if is_l(l):
        for x in l:
            if is_l(x):
                if len(x)==2 and not is_l(x[0]) and not is_l(x[1]):
                    yield x
                else:
                    yield from iter_minmaxs(x)


class PhilaPlots(DashFigureFactory):
    def __init__(self, df=None):
        super().__init__()
        self.df = fig_data() if df is None else df

    def filter(self, filter_data={}, with_query=False):
        if not filter_data:
            ff=self
            q=''
        else:
            df = self.df.sample(frac=1)
            ql=[]
            for k,v in filter_data.items():
                if is_l(v):
                    q = ' | '.join(
                        f'({minv}<={k}<={maxv})'
                        for minv,maxv in iter_minmaxs(v)
                    )
                elif type(v)==str:
                    q=f'{k}=="{v}"'
                ql.append(f'({q})')
            q=' & '.join(ql)
            df = df.query(q) if q else df
            ff=PhilaPlots(df=df)
        return (ff,q) if with_query else ff
    
    def plot_biplot(self, x_axis, y_axis, qual_col):
        return px.scatter(
            self.df,
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
    
    def plot_parcoords(self, cols=None):
        if not cols: cols=get_nonelectoral_cols()
        return px.parallel_coordinates(
            self.df[cols]
        )
    
    





class Philadata(DashComponent):
    def __init__(self):
        super().__init__()
        self.ff=PhilaPlots()


    ### INPUTS

    @cached_property
    def x_axis(self):
        return self._select_axis(
            id='x-axis', 
            placeholder='Select column for X-axis', 
            value='edu_attain'
        )
    
    @cached_property
    def y_axis(self):
        return self._select_axis(
            id='y-axis',
            placeholder='Select column for Y-axis',
            value='PRESIDENT OF THE UNITED STATES-DEM_BERNIE SANDERS'
        )
        
    @cached_property
    def qual_col(self):
        return self._select_axis(
            cols=get_qual_cols(),
            id='qual-col',
            label='Color by',
            placeholder='Select column for color',
            value='largest_race'
        )
    
    def _select_axis(self, id='axis', value='', cols=None, **kwargs):
        if cols is None: cols = get_nonelectoral_cols() + get_electoral_cols()
        options = [dict(label=x.title().replace('_',' '), value=x) for x in cols]
        return dbc.Select(
            options=options,
            value=value,
        )
    ####


    ### GRAPHS
    
    @cached_property
    def graph_biplot(self): return dcc.Graph()
    @cached_property
    def graph_parcoord(self): return dcc.Graph(figure=self.ff.plot_parcoords())
    @cached_property
    def desc_query(self): return html.Div()

    @cached_property
    def filter_data(self): return dcc.Store(id='filter_data')

    ### LAYOUT

    def layout(self):
        return dbc.Container(
            dbc.Row([
                dbc.Col(
                    width=3,
                    class_name='layout-col-left',
                    children=[
                        self.y_axis,
                        self.x_axis,
                        self.qual_col,
                        self.filter_data
                    ]
                ),

                dbc.Col(
                    width=9,
                    children=[
                        self.graph_biplot,
                        self.graph_parcoord,
                        self.desc_query,
                    ]
                )
            ]),
        )
    

    ### CALLBACKS
    def component_callbacks(self, app):
        @app.callback(    
            Output(self.filter_data, "data"),
            Input(self.graph_parcoord, 'restyleData'),
            State(self.filter_data, "data"),
        )
        def parcoord_filter_selected(restyledata, filter_data):
            print('!?!?!/')
            if filter_data is None: filter_data = {}
            if restyledata and type(restyledata) is list:
                for d in restyledata:
                    if type(d) is dict:
                        for k,v in d.items():
                            if k.startswith('dimensions['):
                                dim_i=int(k.split('dimensions[',1)[1].split(']')[0])
                                dim = self.graph_parcoord.figure.data[0].dimensions[dim_i]
                                key = dim.label
                                filter_data[key]=v
            print(filter_data)
            return filter_data

        @app.callback(    
            [
                Output(self.graph_biplot, "figure"),
                Output(self.desc_query, "children"),
            ],
            [
                Input(self.filter_data, "data"),
                Input(self.x_axis,'value'),
                Input(self.y_axis,'value'),
                Input(self.qual_col,'value'),
            ]
        )
        def graph_updated(filter_data, x_axis, y_axis, qual_col):
            if filter_data is None: filter_data={}
            fff,qstr=self.ff.filter(filter_data, with_query=True)

            return (
                fff.plot_biplot(
                    x_axis=x_axis,
                    y_axis=y_axis,
                    qual_col=qual_col
                ),
                qstr
            )

    

if __name__ == "__main__":
    app = DashApp(
        Philadata(), 
        # querystrings=True, 
        bootstrap=True,
    )

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


