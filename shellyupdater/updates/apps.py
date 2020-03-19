# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.apps import AppConfig
from django.conf import settings
from shellyupdater.mqtt import client

logger = logging.getLogger()


class UpdatesConfig(AppConfig):
    name = 'updates'

    def ready(self):
        def on_msg_announce(self, userdata, msg):
            from updates.shelly_handler import put_shelly_json
            logger.debug(msg.payload.decode('utf-8'))
            put_shelly_json(msg.payload.decode('utf-8'))

        def on_device_online(self, userdata, msg):
            from updates.shelly_handler import update_shelly_online
            logger.debug(msg.payload.decode('utf-8'))
            update_shelly_online(topic=msg.topic, status=msg.payload.decode('utf-8'))


        logger.info("App is up")
        mqttclient = client.getMQTTClient()
        mqttclient.message_callback_add(settings.MQTT_SHELLY_ANNOUNCE_TOPIC, on_msg_announce)
        mqttclient.message_callback_add(settings.MQTT_SHELLY_BASE_TOPIC + "+/online", on_device_online)
