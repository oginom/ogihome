#!bin/env python3
#-*- coding:utf-8 -*-

from datetime import datetime, timedelta
import os, sys

from dotenv import load_dotenv
import paho.mqtt.client as mqtt

# FIXME: something cooler
sys.path.append(os.path.join(os.path.dirname(__file__), '../logger'))
print(sys.path)
import db

load_dotenv()

LOG_INTERVAL = int(os.getenv('LOG_INTERVAL'))

data = {}
data_s = {}

def cid_sp(cid):
    d = {
        '38FFAFC40A24': 'room',
        '704532C40A24': 'out',
    }
    if cid in d:
        return d[cid]
    return cid

bef = datetime.now()
lim_interval = timedelta(seconds=LOG_INTERVAL)
lim_range = timedelta(hours=24)
dt_s = timedelta(seconds=LOG_INTERVAL)

def loaddata():
    global lim_range
    start = datetime.now() - lim_range
    loaded = db.fetchall("data", start=start)

    data.clear()
    data_s.clear()
    for (t, topic, value) in loaded:
        if topic not in data:
            data[topic] = []
        data[topic].append((t, value))
        if topic not in data_s:
            data_s[topic] = []
        data_s[topic].append((t, value))

# -*- coding: utf-8 -*-
import dash
#import dash_core_components as dcc
from dash import dcc
#import dash_html_components as html
from dash import html

from dash.dependencies import Input, Output

import plotly
import plotly.subplots as subplt

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='OGIIoT HOME'),

    html.Div(children='''
        OGIIoT HOME sensor data visualizer (using Arduino, ESP32, MQTT, Mosquitto, Paho, Python, Plotly Dash)
    '''),

    dcc.Graph(
        id='live-update-graph',
    ),
    dcc.Interval(
            id='interval-component',
            interval=10*1000,
            n_intervals=0
        )
])


@app.callback(
    Output('live-update-graph', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_graph_live(interval):
    loaddata()

    topic_data = {}
    for topic in data_s:
        sp = topic.split("/")
        topic_name = sp[-1] if len(sp) > 0 else topic
        topic_legend = f"{cid_sp(sp[-2])} {sp[-1]}" if len(sp) > 1 else topic
        if topic_name not in topic_data:
            topic_data[topic_name] = []
        topic_data[topic_name].append({
            'x': [d[0] for d in data_s[topic]],
            'y': [d[1] for d in data_s[topic]],
            'name': topic_legend,
        })

    rs = (len(topic_data) + 1) // 2
    h = rs * 300
    vs = 0.3 / max(1, rs)
    if rs < 1:
        return
    fig = subplt.make_subplots(rows=rs, cols=2, vertical_spacing=vs)
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 10
    }
    fig['layout']['legend'] = {'x': 1, 'y': 0, 'xanchor': 'right'}
    fig['layout']['height'] = h

    for i, (topic, data) in enumerate(topic_data.items()):
        f_i = i // 2
        f_j = i % 2
        for series in data:
            fig.append_trace({
                'x': series['x'],
                'y': series['y'],
                'name': series['name'],
                'legendgroup': str(i),
                'mode': 'lines+markers',
                'type': 'scatter'
            }, row=f_i+1, col=f_j+1)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
