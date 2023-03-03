#!bin/env python3
#-*- coding:utf-8 -*-

from datetime import datetime, timedelta
import os

from dotenv import load_dotenv
import paho.mqtt.client as mqtt

import db

load_dotenv()

MQTT_HOST = os.getenv('MQTT_HOST')
MQTT_PORT = int(os.getenv('MQTT_PORT'))
MQTT_KEEP_ALIVE = int(os.getenv('MQTT_KEEP_ALIVE'))

# ログデータを保存する間隔 (全データだと容量がやばいので)
LOG_INTERVAL = int(os.getenv('LOG_INTERVAL'))

# last logged time
data = {}

dt_s = timedelta(seconds=LOG_INTERVAL)

def loaddata():
    start = datetime.now() - dt_s
    loaded = db.fetchall("data", start=start)
    for (t, topic, value) in loaded:
        if topic not in data:
            data[topic] = t
        else:
            data[topic] = max(t, data[topic])

def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    try:
        t = datetime.now()
        if msg.topic not in data or data[msg.topic] + dt_s <= t:
            data[msg.topic] = t
            db.insert("data", t, msg.topic, float(msg.payload.decode('utf-8')))
    except Exception as e:
        print(str(e))
        pass

if __name__ == '__main__':
    loaddata()

    mqttc = mqtt.Client()
    mqttc.on_message = on_message  # メッセージ受信時に実行するコールバック関数設定
    mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEP_ALIVE)
    mqttc.subscribe("#")
    mqttc.loop_forever()  # 永久ループ
