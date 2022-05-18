#!bin/env python3
#-*- coding:utf-8 -*-

import paho.mqtt.client as mqtt
import time

# MQTT Broker
MQTT_HOST = "192.168.11.105"       # brokerのアドレス
#MQTT_HOST = "localhost"       # brokerのアドレス
MQTT_PORT = 1883                # brokerのport
MQTT_KEEP_ALIVE = 60            # keep alive

# broker接続時
def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))

from datetime import datetime, timedelta

mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEP_ALIVE)

import socket
import subprocess
import json

hostname = socket.gethostname()

def get_val():
    data = subprocess.check_output(['sudo', 'python3', '-m', 'mh_z19'])
    data = data.decode('utf-8')
    data = json.loads(data)['co2']
    return data


if __name__ == '__main__':
    mqttc.loop_start()

    while True:
        try:
            val = get_val()
            print(val)
            mqttc.publish('ogiiot/data/{}/co2'.format(hostname), val)
        except:
            print('err')
        time.sleep(10)

