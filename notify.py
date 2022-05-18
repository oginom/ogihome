#!bin/env python3
#-*- coding:utf-8 -*-

from datetime import datetime, timedelta

import sys
import os

import paho.mqtt.client as mqtt

sys.path.append('/home/pi/ogidata/helper')

import push
push.push('ogihome', 'debug', 'start watch')

# MQTT Broker
MQTT_HOST = "192.168.11.105"       # brokerのアドレス
#MQTT_HOST = "localhost"       # brokerのアドレス
MQTT_PORT = 1883                # brokerのport
MQTT_KEEP_ALIVE = 60            # keep alive

data = {
        'co2': [],
        'temperature': [],
        'humidity': [],
}

co2_over = False
co2_th = 1000

humidity_under = False
humidity_th = 30

temperature_over = False
temperature_th = 29

# broker接続時
def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))

#メッセージ受信時
def on_message(mqttc, obj, msg):
    global co2_over, co2_th, humidity_under, humidity_th, temperature_over, temperature_th
    # print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    try:
        if 'co2' in msg.topic:
            val = float(msg.payload)
            data['co2'].append(val)
            if len(data['co2']) >= 10:
                data['co2'] = data['co2'][-10:]
                if co2_over:
                    if max(data['co2']) < co2_th:
                        co2_over = False
                        print('co2_over end')
                else:
                    if min(data['co2']) > co2_th:
                        co2_over = True
                        print('co2_over begin')
                        push.push('ogihome', 'info', f'CO2が {co2_th} ppm を超えました！')
        if 'temperature' in msg.topic:
            val = float(msg.payload)
            data['temperature'].append(val)
            if len(data['temperature']) >= 10:
                data['temperature'] = data['temperature'][-10:]
                if temperature_over:
                    if max(data['temperature']) < temperature_th:
                        temperature_over = False
                        print('temperature_over end')
                else:
                    if min(data['temperature']) > temperature_th:
                        temperature_over = True
                        print('temperature_over begin')
                        push.push('ogihome', 'info', f'室温が {temperature_th} ℃ を超えました！')
        if 'humidity' in msg.topic:
            val = float(msg.payload)
            data['humidity'].append(val)
            if len(data['humidity']) >= 10:
                data['humidity'] = data['humidity'][-10:]
                if humidity_under:
                    if min(data['humidity']) > humidity_th:
                        humidity_under = False
                        print('humidity_under end')
                else:
                    if max(data['humidity']) < humidity_th:
                        humidity_under = True
                        print('humidity_under begin')
                        push.push('ogihome', 'info', f'湿度が {humidity_th} ％を下回りました！')

    except:
        pass


if __name__ == '__main__':
    mqttc = mqtt.Client()
    mqttc.on_message = on_message  # メッセージ受信時に実行するコールバック関数設定
    mqttc.on_connect = on_connect
    mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEP_ALIVE)
    mqttc.subscribe("#")
    mqttc.loop_forever()  # 永久ループ

