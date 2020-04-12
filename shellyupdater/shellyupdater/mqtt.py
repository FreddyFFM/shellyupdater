# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import paho.mqtt.client as mqtt
from django.conf import settings
from datetime import datetime

logger = logging.getLogger()
mqtt_client = None


def set_mqttclient(client):
    global mqtt_client
    mqtt_client = client


def get_mqttclient():
    return mqtt_client


class MQTTClient():

    mqttclient = None

    def __init__(self):
        def on_connect(client, userdata, flags, rc):
            logger.debug("MQTT: Connected with flags [%s] rtn code [%d]" % (flags, rc))

        def on_log(client, userdata, level, buf):
            logger.debug("MQTT: " + str(buf))
            print("MQTT LOG - " + str(datetime.now()) + ": " + buf + " - ClientID: " + clientid)
            pass

        clientid = str(hash(datetime.now()))
        self.mqttclient = mqtt.Client("ShellyUpdater_" + clientid)  # create new instance
        print("MQTT LOG - " + str(datetime.now()) + ": Connecting to broker" + settings.MQTT_BROKER_ADDRESS)

        self.mqttclient.on_connect = on_connect
        self.mqttclient.on_log = on_log
        self.mqttclient.enable_logger(logger)
        self.mqttclient.username_pw_set(username=settings.MQTT_USERNAME, password=settings.MQTT_PASSWORD)
        rc = self.mqttclient.connect(host=settings.MQTT_BROKER_ADDRESS)  # connect to broker
        if rc == 0:
            print("MQTT LOG - " + str(datetime.now()) + ": Connected to MQTT")
            self.mqttclient.subscribe(settings.MQTT_SHELLY_ANNOUNCE_TOPIC)
            self.mqttclient.subscribe(settings.MQTT_SHELLY_BASE_TOPIC + "+/online")
        else:
            print("MQTT LOG - " + str(datetime.now()) + ": Connection error " + rc)

    def startMQTTloop(self):
        self.mqttclient.loop_start()

    def getMQTTClient(self):
        return self.mqttclient
