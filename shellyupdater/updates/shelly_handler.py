"""
This module handles all Shelly update/info functions and the communication via MQTT
"""

import json
import logging

from .models import Shellies, ShellySettingUpdates
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

    # if Shelly not exists create a new in DB
    if id:
        if Shellies.objects.filter(shelly_id=id).exists():
            shelly = Shellies.objects.get(shelly_id=id)
            logger.debug(
                "SHELLY LOG - " + str(datetime.now()) + ": SHELLY EXISTENT - ID: " + str(id))
        else:
            shelly = Shellies()
            shelly.shelly_id = id
            shelly.shelly_last_online = timezone.now()
            logger.info(
                "SHELLY LOG - " + str(datetime.now()) + ": SHELLY NEW - ID: " + str(id))

        shelly.shelly_type = (id.split('-')[0]).upper()
        shelly.shelly_new_fw = fw_update

        # Apply firmware update when available an initiated
        # This is already done when device announces online state
        # if fw_update and shelly.shelly_do_update:
        #     logger.info(
        #         "SHELLY LOG - " + str(datetime.now()) + ": SHELLY PERFORM UPDATE - ID: " + str(id))
        #     perform_update_http(shelly=shelly)

        # update firmware information and update status
        if not fw_update and shelly.shelly_do_update and fw_ver.split("@")[0] != shelly.shelly_fw_version_old:
            logger.info(
                "SHELLY LOG - " + str(datetime.now()) + ": SHELLY UPDATE DONE - ID: " + str(id))
            shelly.shelly_do_update = False
            current_dt = datetime.now().strftime("%d.%m.%Y %H:%M")
            shelly.last_status = current_dt + ": Update OK"

        if name:
            shelly.shelly_name = name
        if mac:
            shelly.shelly_mac = mac
        if ip:
            shelly.shelly_ip = ip
        if fw_ver:
            shelly.shelly_fw_version = fw_ver.split("@")[0]

        shelly.save()


def put_shelly_json(payload=None):
    """
    Convert MQTT JSON to Dict and save to DB
    :param payload:
    :return:
    """
    shelly = json.loads(payload)
    put_shelly(id=shelly["id"], name=shelly["id"], mac=shelly["mac"], ip=shelly["ip"], fw_update=shelly["new_fw"], fw_ver=shelly["fw_ver"])
    logger.info(
        "SHELLY LOG - " + str(datetime.now()) + ": SHELLY ANNOUNCED - ID: " + str(shelly["id"]) + ", " + str(
            payload))


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

        if Shellies.objects.filter(shelly_id=shelly_id).exists():
            logger.info(
                "SHELLY LOG - " + str(datetime.now()) + ": SHELLY ONLINE - ID: " + str(shelly_id) + ", " + str(shelly_online))
            shelly = Shellies.objects.get(shelly_id=shelly_id)

            current_ts = timezone.now()
            shelly.shelly_online = shelly_online
            shelly.shelly_last_online = current_ts

            diff = current_ts - shelly.shelly2infos.last_change_ts
            shellyupdates = ShellySettingUpdates.objects.filter(shelly_id=shelly, shelly_settings_applied=False,
                                                                shelly_settings_delete=False).exists()
            # if shelly_online and has updates or settings-changes or needs current settings catch
            if shelly_online and ((0 < settings.MAX_INFO_DAYS <= diff.days) or shelly.shelly_do_update or shellyupdates):
                # start available and initiated updates
                if shelly.shelly_do_update:
                    logger.info(
                        "SHELLY LOG - " + str(datetime.now()) + ": SHELLY PERFORM UPDATE - ID: " + str(shelly))
                    perform_update_http(shelly=shelly)

                # shelly hs setting updates
                elif shellyupdates:
                    apply_shelly_settings(shelly=shelly)

                # need to catch settings and status
                else:
                    logger.info(
                        "SHELLY LOG - " + str(datetime.now()) + ": SHELLY CATCH INFOS - ID: " + str(shelly_id))
                    get_shelly_info(shelly_id=shelly_id)

            shelly.save()
