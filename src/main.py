import numpy as np
import pandas as pd
import streamlit as st
from dateutil.relativedelta import relativedelta

import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots

import json
import requests

config_path = './src/config.json'
with open(config_path) as f: #Loading configuration file to a dict
    config = json.load(f)

with open(config['data_geo']) as f: # loading geo info from data/geo_init.json
    data_geo = json.load(f)

content_dict = {}
for page in config['data_content'].keys(): # loading page text for each page and saving to a dict
    with open(config['data_content'][page], 'r') as f:
        content_dict[page] = f.read()


def convert2daily(df:pd.DataFrame,cols:str):
    '''
    :param df: Data Frame I want to convert columns to daily
    :param cols: Columns with Cummulative Sum that I wawnt to change to daily
    :return: DataFrame with daily losses
    '''
    new_col = cols+'_daily'
    df[new_col] = df[cols].diff()
    df.loc[0,new_col]= df.loc[0,cols]
    df[new_col].fillna(0)
    return df

def monthly_count(df):
    monthly_counts = df.groupby([df['date'].dt.year, df['date'].dt.month])[
        'personnel_daily'].sum()
    test_df = pd.DataFrame({
        'Year': monthly_counts.index.get_level_values(0),
        'Month': monthly_counts.index.get_level_values(1),
        'count': monthly_counts.values
    })
    test_df['Month'] = pd.to_datetime(test_df['Month'], format='%m')
    test_df['Month'] = test_df['Month'].dt.strftime('%B')

    return test_df
def line_plot(df,col,slider:bool):
    fig = px.bar(df, x='date', y=col,title='To date Deaths')
    if slider:
        fig.update_xaxes(
            rangeslider_autorange=True,
            rangeselector_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
    fig.update_layout(xaxis_title = 'Date',yaxis_title='Deaths')
    return fig


#Lets load actual data

period_last = config['period_last']
df_geo = pd.DataFrame.from_dict(data_geo)

df_oryx = pd.DataFrame(requests.get(config['url']['oryx']).json())
df_personnel = pd.DataFrame(requests.get(config['url']['personnel']).json())
df_equipment = pd.DataFrame(requests.get(config['url']['equipment']).json())

df_personnel['date'] = pd.to_datetime(df_personnel['date'],format='%Y-%m-%d')
df_personnel['POW']= df_personnel['POW'].fillna(0)
df_personnel = convert2daily(df_personnel,'personnel')

last_day = df_equipment.day.iloc[-1]


st.set_page_config(page_title='War-Losses', layout="wide")
with st.container():
    _, col100, _ = st.columns((1,2,1))
    with col100:
        st.markdown('### Personnel Losses during the 2022 russian invasion of Ukraine')

    _, col101, _ = st.columns((.05,1,.05))
    with col101:
        fig = line_plot(df_personnel, 'personnel_daily', slider=True)
        fig.update_layout(
            height=800,
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    _, col102, _ = st.columns((.05,1,.05))
    with col102:
        tree_df = monthly_count(df_personnel)

        fig = px.treemap(
            tree_df,
            path=[px.Constant('All'), 'Year', 'Month'],
            values='count',
            title='Yearly Death Destribution'
        )

        fig.update_layout(
            height=800,
            margin=dict(t=50, l=25, r=25, b=25))
        st.plotly_chart(fig, use_container_width=True)

    _, col103, _ = st.columns((.05, 1, .05))
    with col103:
        monthly_df = monthly_count(df_personnel)
        fig = px.bar(data_frame=monthly_df, x='Month', y='count',title='Deadliest Months Overall')
        fig.update_layout(
            height=800,
            margin=dict(t=50, l=25, r=25, b=25))
        st.plotly_chart(fig, use_container_width=True)


