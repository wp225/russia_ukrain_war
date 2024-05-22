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

config_path = 'config.json'
with open(config_path) as f: #Loading configuration file to a dict
    config = json.load(f)

with open(config['data_geo']) as f: # loading geo info from data/geo_init.json
    data_geo = json.load(f)

content_dict = {}
for page in config['data_content'].keys(): # loading page text for each page and saving to a dict
    with open(config['data_content'][page], 'r') as f:
        content_dict[page] = f.read()


#Lets load actual data
period_last = config['period_last']
df_geo = pd.DataFrame.from_dict(data_geo)
