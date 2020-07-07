"""
This module handles the MQTT communication
"""

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import paho.mqtt.client as mqtt
from django.conf import settings
from datetime import datetime

logger = logging.getLogger(__name__)
mqtt_client = None


def set_mqttclient(client):
    """
    Set MQTT Client for global usage
    :param client:
    :return:
    """
    global mqtt_client
    mqtt_client = client


def get_mqttclient():
    """
    Return client for global usage
    :return:
    """
    return mqtt_client


class MQTTClient():
    """
    Create the MQTT client
    """

    mqttclient = None

    def __init__(self):
        """
        Initialize the MQTT client
        """
        def on_connect(client, userdata, flags, rc):
            """
            Log the connect
            :param client:
            :param userdata:
            :param flags:
            :param rc:
            :return:
            """
            logger.debug("MQTT LOG - " + str(datetime.now()) + ": CONNECTED with flags [%s] rtn code [%d]" % (flags, rc))

        clientid = str(hash(datetime.now()))
        self.mqttclient = mqtt.Client("ShellyUpdater_" + clientid)  # create new instance
        logger.info("MQTT LOG - " + str(datetime.now()) + ": Connecting to broker" + settings.MQTT_BROKER_ADDRESS)

        try:
            self.mqttclient.on_connect = on_connect
            self.mqttclient.username_pw_set(username=settings.MQTT_USERNAME, password=settings.MQTT_PASSWORD)
            rc = self.mqttclient.connect(host=settings.MQTT_BROKER_ADDRESS)  # connect to broker
            if rc == 0:
                logger.info("MQTT LOG - " + str(datetime.now()) + ": Connected to MQTT")
            else:
                logger.error("MQTT LOG - " + str(datetime.now()) + ": Connection error " + rc)
        except Exception as e:
            logger.error("MQTT LOG - " + str(datetime.now()) + ": Exception " + str(e))

    def startMQTTloop(self):
        """
        Start the MQTT logging
        :return:
        """
        self.mqttclient.loop_start()

    def getMQTTClient(self):
        """
        return reference to MQTT client
        :return:
        """
        return self.mqttclient
