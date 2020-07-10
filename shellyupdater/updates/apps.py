"""
This module provides actions that are executed after the application is fully loaded
E.g. starting MQTT
"""

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging, os

from django.apps import AppConfig
from django.conf import settings
from shellyupdater.mqtt import MQTTClient, set_mqttclient
from datetime import datetime

logger = logging.getLogger()


def start_MQTT():
    """
    Start MQTT after application is loaded
    :return:
    """

    def on_msg_announce(self, userdata, msg):
        """
        Log Shelly announcements and handle them
        :param self:
        :param userdata:
        :param msg:
        :return:
        """
        from updates.shelly_handler import put_shelly_json
        logger.debug("MQTT LOG - " + str(datetime.now()) + ": DEVICE ANNOUNCE: "+ msg.payload.decode('utf-8'))
        put_shelly_json(msg.payload.decode('utf-8'))

    def on_device_online(self, userdata, msg):
        """
        Log Shelly online announcements and handle them
        :param self:
        :param userdata:
        :param msg:
        :return:
        """
        from updates.shelly_handler import update_shelly_online
        logger.debug("MQTT LOG - " + str(datetime.now()) + ": DEVICE ONLINE: " + msg.payload.decode('utf-8'))
        update_shelly_online(topic=msg.topic, status=msg.payload.decode('utf-8'))

    def on_battery_change(self, userdata, msg):
        """
        Log Shelly battery changes
        :param self:
        :param userdata:
        :param msg:
        :return:
        """
        from updates.shelly_handler import update_shelly_battery
        logger.debug("MQTT LOG - " + str(datetime.now()) + ": DEVICE BATTERY UPDATE: " + msg.payload.decode('utf-8'))
        update_shelly_battery(topic=msg.topic, status=msg.payload.decode('utf-8'))

    mqttclient = MQTTClient().getMQTTClient()
    set_mqttclient(mqttclient)
    mqttclient.loop_start()

    # Subscribe to global announcement topic and Shelly specific online topics
    if not mqttclient.is_connected():
        mqttclient.loop_stop()
        logger.info("MQTT LOG - " + str(datetime.now()) + ": Disconnected from MQTT")
    else:
        mqttclient.subscribe(settings.MQTT_SHELLY_ANNOUNCE_TOPIC)
        logger.info("MQTT LOG - " + str(datetime.now()) + ": Subscribed to " + settings.MQTT_SHELLY_ANNOUNCE_TOPIC)
        mqttclient.subscribe(settings.MQTT_SHELLY_BASE_TOPIC + "+/online")
        logger.info(
            "MQTT LOG - " + str(datetime.now()) + ": Subscribed to " + settings.MQTT_SHELLY_BASE_TOPIC + "+/online")
        mqttclient.subscribe(settings.MQTT_SHELLY_BASE_TOPIC + "+/+/battery")
        logger.info(
            "MQTT LOG - " + str(
                datetime.now()) + ": Subscribed to " + settings.MQTT_SHELLY_BASE_TOPIC + "+/sensor/battery")

        # Add callbacks for topics
        mqttclient.message_callback_add(settings.MQTT_SHELLY_ANNOUNCE_TOPIC, on_msg_announce)
        logger.debug("MQTT LOG - " + str(datetime.now()) + ": Added callback to " + settings.MQTT_SHELLY_ANNOUNCE_TOPIC)
        mqttclient.message_callback_add(settings.MQTT_SHELLY_BASE_TOPIC + "+/online", on_device_online)
        logger.debug("MQTT LOG - " + str(datetime.now()) + ": Added callback to " + settings.MQTT_SHELLY_BASE_TOPIC + "+/online")
        mqttclient.message_callback_add(settings.MQTT_SHELLY_BASE_TOPIC + "+/sensor/battery", on_battery_change)
        logger.debug(
            "MQTT LOG - " + str(datetime.now()) + ": Added callback to " + settings.MQTT_SHELLY_BASE_TOPIC + "+/sensor/battery")


class UpdatesConfig(AppConfig):
    name = 'updates'

    def ready(self):
        if os.environ.get('RUN_MAIN', None) != 'true':
            return

        # Start MQTT after application is fully loaded
        start_MQTT()

        logger.info("App is up")
