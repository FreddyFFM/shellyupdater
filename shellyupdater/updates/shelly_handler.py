"""
This module handles all Shelly update/info functions and the communication via MQTT
"""

import json
import logging
import time
import pytz

from shellyupdater.mqtt import MQTTClient
from .models import Shellies, ShellySettingUpdates, ShellySettings
from django.utils import timezone
from datetime import datetime
from .shelly_http_handler import get_shelly_info, perform_update_http, apply_shelly_settings
from django.conf import settings


logger = logging.getLogger(__name__)


def put_shelly(id=None, name="", mac="", ip="", fw_update=False, fw_ver=""):
    """
    Save Shelly Information to Database
    Apply Updates if applicable
    :param id:
    :param name:
    :param mac:
    :param ip:
    :param fw_update:
    :param fw_ver:
    :return:
    """

    if id:
        logger.info(
            "SHELLY LOG - " + str(datetime.now()) + ": SHELLY ONLINE - ID: " + str(id))

        # if Shelly not exists create a new in DB
        if Shellies.objects.filter(shelly_id=id).exists():
            shelly = Shellies.objects.get(shelly_id=id)
            logger.debug(
                "SHELLY LOG - " + str(datetime.now()) + ": SHELLY EXISTENT - ID: " + str(id))
        else:
            shelly = Shellies()
            shelly.shelly_id = id
            shelly.shelly_type = (id.split('-')[0]).upper()
            logger.info(
                "SHELLY LOG - " + str(datetime.now()) + ": SHELLY NEW - ID: " + str(id))

        current_ts = timezone.now()

        shelly.shelly_last_online = current_ts
        shelly.shelly_new_fw = fw_update

        # update firmware information and update status
        if not fw_update and shelly.shelly_do_update and fw_ver.split("@")[0] != shelly.shelly_fw_version_old.split("@")[0]:
            logger.info(
                "SHELLY LOG - " + str(datetime.now()) + ": SHELLY UPDATE DONE - ID: " + str(id))
            shelly.shelly_do_update = False
            current_dt = datetime.now().strftime("%d.%m.%Y %H:%M")
            shelly.last_status = current_dt + ": Update OK"

        elif shelly.shelly_do_update:
            shelly.shelly_fw_version_old = shelly.shelly_fw_version
            logger.info(
                "SHELLY LOG - " + str(datetime.now()) + ": SHELLY PERFORM UPDATE - ID: " + str(shelly))
            perform_update_http(shelly=shelly)

        if name:
            shelly.shelly_name = name
        if mac:
            shelly.shelly_mac = mac
        if ip:
            shelly.shelly_ip = ip
        if fw_ver:
            shelly.shelly_fw_version = fw_ver.split("@")[0]

        shelly.save()

        logger.debug(
            "SHELLY LOG - " + str(datetime.now()) + ": SHELLY SAVED: " + str(id))

        try:
            diff = current_ts - shelly.shelly2infos.last_change_ts
            shellyupdates = ShellySettingUpdates.objects.filter(shelly_id=shelly, shelly_settings_applied=False,
                                                                shelly_settings_delete=False).exists()
        except:
            logger.debug(
                "SHELLY LOG - " + str(datetime.now()) + ": Shelly Settings not existing yet: " + str(id))
            shellyupdates = None
            diff = current_ts - datetime(1970, 1, 1, tzinfo=pytz.timezone(settings.TIME_ZONE))
            pass

        # shelly hs setting updates
        if not shelly.shelly_do_update and shellyupdates:
            apply_shelly_settings(shelly=shelly)

        # need to catch settings and status
        if not (shelly.shelly_do_update or shellyupdates) and 0 < settings.MAX_INFO_DAYS <= diff.days:
            logger.info(
                "SHELLY LOG - " + str(datetime.now()) + ": SHELLY CATCH INFOS - ID: " + str(id))
            get_shelly_info(shelly_id=id)


def put_shelly_json(payload=None):
    """
    Convert MQTT JSON to Dict and save to DB
    :param payload:
    :return:
    """
    try:
        shelly = json.loads(payload)
        put_shelly(id=shelly["id"], name=shelly["id"], mac=shelly["mac"], ip=shelly["ip"], fw_update=shelly["new_fw"], fw_ver=shelly["fw_ver"])
        logger.info(
            "SHELLY LOG - " + str(datetime.now()) + ": SHELLY ANNOUNCED - ID: " + str(shelly["id"]) + ", " + str(
                payload))
    except Exception as e:
        logger.error(
            "SHELLY LOG - " + str(datetime.now()) + ": SHELLY PUT Exception: " + str(e))


def update_shelly_online(topic=None, status=None):
    """
    Update Shelly Online Information
    Apply or mark Updates if applicable
    :param topic:
    :param status:
    :return:
    """
    if topic:
        shelly_id = topic.split('/')[1]
        if status == 'true':
            shelly_online = True
        else:
            shelly_online = False

        if Shellies.objects.filter(shelly_id=shelly_id).exists() and not shelly_online:
            logger.info(
                "SHELLY LOG - " + str(datetime.now()) + ": SHELLY OFFLINE - ID: " + str(shelly_id))
            shelly = Shellies.objects.get(shelly_id=shelly_id)

            current_ts = timezone.now()
            shelly.shelly_online = shelly_online
            shelly.shelly_last_online = current_ts

            shelly.save()


def update_shelly_battery(topic=None, status=None):
    """
    Update Shelly Online Information
    Apply or mark Updates if applicable
    :param topic:
    :param status:
    :return:
    """
    if topic and status:
        shelly_id = topic.split('/')[1]

        logger.info(
            "SHELLY LOG - " + str(datetime.now()) + ": SHELLY BATTERY UPDATE - ID: " + str(shelly_id) + ", " + str(
                status))

        if ShellySettings.objects.filter(shelly_id__shelly_id=shelly_id).exists():
            shellySettings = ShellySettings.objects.get(shelly_id__shelly_id=shelly_id)

            shellySettings.shelly_battery_percent = status
            shellySettings.save()
        else:
            if Shellies.objects.filter(shelly_id=shelly_id).exists():
                shelly = Shellies.objects.get(shelly_id=shelly_id)

                shellySettings = ShellySettings()
                shellySettings.shelly_id = shelly

                shellySettings.shelly_battery_percent = status
                shellySettings.save()


def do_mqtt_announce():
    mqttclient = MQTTClient().getMQTTClient()

    logger.info(
        "SHELLY LOG - " + str(datetime.now()) + ": SHELLY MASS ANNOUNCE")

    i = 1
    while True:
        logger.debug("MQTT LOG - " + str(
            datetime.now()) + ": Publish announce to " + settings.MQTT_SHELLY_COMMAND_TOPIC + " - retry " +
                     str(i))

        result = mqttclient.publish(settings.MQTT_SHELLY_COMMAND_TOPIC, "announce")

        logger.debug("MQTT LOG - " + str(
            datetime.now()) + ": Published announce with result " + str(result.rc))

        if result.rc == 0:
            logger.info(
                "SHELLY LOG - " + str(datetime.now()) + ": SHELLY MASS ANNOUNCE SUCCESSFUL")
            return True
        if i > 10:
            logger.error(
                "SHELLY LOG - " + str(datetime.now()) + ": MQTT NOT AVAILABLE")

            return False

        i = i + 1
        time.sleep(1)
