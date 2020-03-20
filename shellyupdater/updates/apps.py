# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging, os

from django.apps import AppConfig
from django.conf import settings
from shellyupdater.mqtt import MQTTClient

logger = logging.getLogger()


class UpdatesConfig(AppConfig):
    name = 'updates'

    def ready(self):
        print(os.environ.get('RUN_MAIN', None))
        if os.environ.get('RUN_MAIN', None) != 'true':
            return

        def on_msg_announce(self, userdata, msg):
            from updates.shelly_handler import put_shelly_json
            logger.debug(msg.payload.decode('utf-8'))
            put_shelly_json(msg.payload.decode('utf-8'))

        def on_device_online(self, userdata, msg):
            from updates.shelly_handler import update_shelly_online
            logger.debug(msg.payload.decode('utf-8'))
            update_shelly_online(topic=msg.topic, status=msg.payload.decode('utf-8'))


        logger.info("App is up")
        mqttclient = MQTTClient().getMQTTClient()
        mqttclient.loop_start()
        mqttclient.message_callback_add(settings.MQTT_SHELLY_ANNOUNCE_TOPIC, on_msg_announce)
        mqttclient.message_callback_add(settings.MQTT_SHELLY_BASE_TOPIC + "+/online", on_device_online)
