import os
import pandas as pd
from functools import lru_cache



#############
# DATA SETUP #
#############

@lru_cache(maxsize=None)
def precinct_data():
    df=pd.read_csv(os.path.join(os.path.dirname(__file__), 'prec_results_demos.csv'))
    df['prec_20'] = df['prec_20'].apply(lambda x: f'{int(x):04}')
    df['ward'] = df['prec_20'].apply(lambda x: x[:2])
    df['prec'] = df['prec_20'].apply(lambda x: x[2:])
    df=df.set_index(['ward','prec']).sort_index()
    df=df[[c for c in df if not (c[0]=='B' and c[1].isdigit())]]
    return df


def corr_data(cols=[]):
    df=precinct_data()
    if cols: df=df[[c for c in df if c in set(cols)]]
    df=df.select_dtypes('number')
    df=df.corr()
    return df


@lru_cache(maxsize=None)
def fig_data():
    df=precinct_data().reset_index()
    for col in get_qual_cols():
        df[col]=df[col].apply(str)
    return df





def get_electoral_cols():
    return [c for c in precinct_data() if c[0]==c[0].upper()]

def get_nonelectoral_cols(quant=None):
    return [
        c 
        for c in precinct_data()
        if c[0]==c[0].lower() and c.split('_')[0] not in {'clust','prec','total'}
        and c+'_share' not in set(precinct_data().columns)
        and (not quant or c not in set(get_qual_cols()))
    ]

@lru_cache
def get_qual_cols():
    o=set(precinct_data().select_dtypes(exclude='number').columns)
    return sorted(list(o))