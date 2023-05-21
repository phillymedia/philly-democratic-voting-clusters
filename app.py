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


class PhilaPlotFactory(DashFigureFactory):
    def __init__(self):
        super().__init__()
        self.df = fig_data()
    
    @cached_property
    def filter_data(self): return dcc.Store(id='filter_data')

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
    




    ###

    
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

    
class Philadata(DashComponent):
    def __init__(self):
        super().__init__()
        self.ff=PhilaPlotFactory()
        self.biplot = PhilaBiplot(self.ff)
        self.parcoord = PhilaParcoord(self.ff)

    def layout(self):
        return dbc.Container(
            dbc.Row([
                dbc.Col(
                    width=3,
                    class_name='layout-col-left',
                    children=[
                        self.ff.y_axis,
                        self.ff.x_axis,
                        self.ff.qual_col,
                        self.ff.filter_data
                    ]
                ),

                dbc.Col(
                    width=9,
                    children=[
                        self.biplot.layout(),
                        self.parcoord.layout(),                        
                    ]
                )
            ]),
        )
    
    def component_callbacks(self, app):
        @app.callback(
            Output(self.ff.x_axis, 'options'),
            [
                Input(self.ff.y_axis,'value'),
                State(self.ff.x_axis,'value')
            ]
        )
        def update_opts(y_axis, x_axis):
            qcols = list(get_nonelectoral_cols(quant=True))
            s = corr_data()[y_axis].loc[qcols].sort_values(ascending=False)
            options = [
                dict(label=f'({cor*100:.3}%) {get_label_str(x)}', value=x)
                for x,cor in zip(s.index, s)
                if cor != 1
                and not x+'_share' in set(s.index)
            ]
            return options



    

class PhilaBiplot(DashComponent):
    def __init__(self, ff):
        super().__init__()

    def layout(self): return self.graph
    
    @cached_property
    def graph(self): return dcc.Graph()
    
    
    def component_callbacks(self, app):
        @app.callback(
            Output(self.graph, 'figure'),
            [
                Input(self.ff.x_axis, 'value'),
                Input(self.ff.y_axis, 'value'),
                Input(self.ff.qual_col, 'value')
            ]
                
        )
        def update(x_axis, y_axis, qual_col):
            return self.ff.plot_biplot(
                x_axis, 
                y_axis, 
                qual_col
            )




class PhilaParcoord(DashComponent):
    def __init__(self, ff):
        super().__init__()
    
    def layout(self): 
        return dbc.Container([self.graph, self.ff.filter_data])
    
    @cached_property
    def graph(self): return dcc.Graph(figure=self.ff.plot_parcoords())
    @property
    def figdata(self):
        return self.graph.figure.data[0]

    def component_callbacks(self, app):
        @callback(    
            Output(self.ff.filter_data, "data"),
            Input(self.graph, 'restyleData'),
            State(self.ff.filter_data, "data"),
        )
        def update(restyledata, filter_data):
            if filter_data is None: filter_data = {}
            if restyledata and type(restyledata) is list:
                for d in restyledata:
                    if type(d) is dict:
                        for k,v in d.items():
                            if k.startswith('dimensions['):
                                dim_i=int(k.split('dimensions[',1)[1].split(']')[0])
                                dim = self.figdata.dimensions[dim_i]
                                key = dim.label
                                filter_data[key]=v
            print(filter_data)
            return filter_data

    

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


