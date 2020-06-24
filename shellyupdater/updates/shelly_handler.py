"""
This module handles all Shelly update/info functions and the communication via MQTT
"""

import json
import time

from .models import Shellies
from django.utils import timezone
from datetime import datetime
from shellyupdater.mqtt import get_mqttclient
from .shelly_http_handler import get_shelly_info, perform_update_http, apply_shelly_settings
from django.conf import settings


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
        else:
            shelly = Shellies()
            shelly.shelly_id = id
            shelly.shelly_last_online = timezone.now()

        shelly.shelly_type = (id.split('-')[0]).upper()
        shelly.shelly_new_fw = fw_update

        # Apply firmware update when available an initiated
        if fw_update and shelly.shelly_do_update:
            perform_update_http(shelly=shelly)

        # update firmware information and update status
        elif not fw_update and shelly.shelly_do_update and fw_ver.split("@")[0] != shelly.shelly_fw_version_old:
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
            shelly = Shellies.objects.get(shelly_id=shelly_id)

            current_ts = timezone.now()
            shelly.shelly_online = shelly_online
            shelly.shelly_last_online = current_ts

            diff = current_ts - shelly.shelly2infos.last_change_ts
            # if shelly is online update settings and status information in DB (after time interval)
            if shelly_online and ((diff.days >= settings.MAX_INFO_DAYS) or shelly.shelly_do_update):
                # start available and initiated updates
                if shelly.shelly_do_update:
                    perform_update_http(shelly=shelly)
                # if no updates apply new settings (if applicable)
                else:
                    apply_shelly_settings(shelly=shelly)

                # catch settings and status
                get_shelly_info(shelly_id=shelly_id)

            shelly.save()
