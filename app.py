#!bin/env python3
#-*- coding:utf-8 -*-

from datetime import datetime, timedelta

import paho.mqtt.client as mqtt

import db

# MQTT Broker
MQTT_HOST = "192.168.11.105"       # brokerのアドレス
#MQTT_HOST = "localhost"       # brokerのアドレス
MQTT_PORT = 1883                # brokerのport
MQTT_KEEP_ALIVE = 60            # keep alive

data = {}
data_s = {}



bef = datetime.now()
lim_interval = timedelta(minutes=10)
lim_range = timedelta(hours=24)
dt_s = timedelta(minutes=10)

def loaddata():
    global lim_range
    start = datetime.now() - dt_s
    loaded = db.fetchall("data", start=start)
    for (t, topic, value) in loaded:
        if topic not in data:
            data[topic] = []
        data[topic].append((t, value))
        if topic not in data_s:
            data_s[topic] = []
        data_s[topic].append((t, value))
loaddata()

# broker接続時
def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))


def lim_data():
    global bef, lim_interval, lim_range
    n = datetime.now()
    if bef + lim_interval < n:
        s = n - lim_range
        for topic in data:
            data[topic] = [x for x in data[topic] if x[0] > s]
        for topic in data_s:
            data_s[topic] = [x for x in data_s[topic] if x[0] > s]
        bef = datetime.now()

#メッセージ受信時
def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    try:
        if msg.topic not in data:
            data[msg.topic] = []
        t = datetime.now()
        data[msg.topic].append((t, float(msg.payload.decode('utf-8'))))

        if msg.topic not in data_s:
            data_s[msg.topic] = []
        t = datetime.now()
        if len(data_s[msg.topic]) < 1 or data_s[msg.topic][-1][0] + dt_s < t:
            data_s[msg.topic].append((t, float(msg.payload.decode('utf-8'))))
            db.insert("data", t, msg.topic, float(msg.payload.decode('utf-8')))
    except:
        pass
    lim_data()

mqttc = mqtt.Client()
mqttc.on_message = on_message  # メッセージ受信時に実行するコールバック関数設定
mqttc.on_connect = on_connect
print('bef conn')
mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEP_ALIVE)
print('aft conn')

mqttc.subscribe("#")
print('aft conn2')

#mqttc.loop_forever()  # 永久ループ

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


@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(interval):
    rs = (len(data_s)-1) // 2 + 1
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

    for i, topic in enumerate(data_s):
        f_i = i // 2
        f_j = i % 2
        fig.append_trace({
            'x': [d[0] for d in data_s[topic]],
            'y': [d[1] for d in data_s[topic]],
            'name': topic,
            'mode': 'lines+markers',
            'type': 'scatter'
        }, f_i+1, f_j+1)

    return fig

if __name__ == '__main__':
    mqttc.loop_start()
    app.run_server(debug=True, host='0.0.0.0')

