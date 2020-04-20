"""
This module handles the http communication to the Shellies
"""

import requests
import json

from datetime import datetime
from django.conf import settings
from .models import Shellies, ShellySettings, ShellySettingUpdates


def get_shelly_info(shelly_id=None):
    """
    Get Shelly settings and status via http and update on DB
    :param shelly_id:
    :return:
    """
    if not shelly_id:
        return False

    if Shellies.objects.filter(shelly_id=shelly_id).exists():
        shelly = Shellies.objects.get(shelly_id=shelly_id)
    else:
        return False

    if ShellySettings.objects.filter(shelly_id=shelly).exists():
        shellySettings = ShellySettings.objects.get(shelly_id=shelly)
    else:
        shellySettings = ShellySettings()
        shellySettings.shelly_id = shelly

    if get_shelly_settings(shelly=shelly, shellySettings=shellySettings) and get_shelly_status(shelly=shelly, shellySettings=shellySettings):
        shellySettings.save()
        shelly.save()
        return True

    return False


def get_shelly_settings(shelly=None, shellySettings=None):
    """
    get the current Shelly settings
    :param shelly:
    :param shellySettings:
    :return:
    """
    if not shelly or not shellySettings:
        return False

    current_dt = datetime.now().strftime("%d.%m.%Y %H:%M")
    try:
        response = requests.get("http://" + shelly.shelly_ip + "/settings",
                            auth=(settings.HTTP_SHELLY_USERNAME, settings.HTTP_SHELLY_PASSWORD), timeout=2)
        if response.status_code == 200:
            shellySettings.shelly_settings_json = json.dumps(json.loads(response.text.strip()), indent=4, sort_keys=True)
            status = current_dt + ": HTTP OK " + str(response.status_code)
            print("HTTP LOG - " + str(datetime.now()) + ": HTTP OK - " + response.url + " - " + str(response.status_code))
        else:
            status = current_dt + ": HTTP Error " + str(response.status_code)
            print("HTTP LOG - " + str(datetime.now()) + ": HTTP Error - " + response.url + " - " + str(response.status_code))
    except requests.exceptions.RequestException as e:
        status = current_dt + ": Exception " + str(e)
        print("HTTP LOG - " + str(datetime.now()) + ": HTTP Exception - " + str(e))

    shellySettings.last_status_settings = status

    return True


def get_shelly_status(shelly=None, shellySettings=None):
    """
    get the current Shelly status
    :param shelly:
    :param shellySettings:
    :return:
    """
    if not shelly or not shellySettings:
        return False

    current_dt = datetime.now().strftime("%d.%m.%Y %H:%M")
    try:
        response = requests.get("http://" + shelly.shelly_ip + "/status",
                                auth=(settings.HTTP_SHELLY_USERNAME, settings.HTTP_SHELLY_PASSWORD), timeout=2)
        if response.status_code == 200:
            status_json = json.loads(response.text.strip())
            shellySettings.shelly_status_json = json.dumps(status_json, indent=4, sort_keys=True)
            if "bat" in status_json:
                shellySettings.shelly_battery_percent = status_json["bat"]["value"]
                shellySettings.shelly_battery_voltage = status_json["bat"]["voltage"]
            if "update" in status_json:
                shelly.shelly_fw_version_new = status_json["update"]["new_version"]
            status = current_dt + ": HTTP OK " + str(response.status_code)
            print(
                "HTTP LOG - " + str(datetime.now()) + ": HTTP OK - " + response.url + " - " + str(response.status_code))
        else:
            status = current_dt + ": HTTP Error " + str(response.status_code)
            print("HTTP LOG - " + str(datetime.now()) + ": HTTP Error - " + response.url + " - " + str(
                response.status_code))
    except requests.exceptions.RequestException as e:
        status = current_dt + ": Exception " + str(e)
        print("HTTP LOG - " + str(datetime.now()) + ": HTTP Exception - " + str(e))

    shellySettings.last_status_status = status

    return True


def perform_update_http(shelly=None):
    """
    Perform a firmware update on Shelly via http
    :param shelly:
    :return:
    """

    if not shelly:
        return False

    current_dt = datetime.now().strftime("%d.%m.%Y %H:%M")
    try:
        response = requests.get("http://" + shelly.shelly_ip + "/ota?update=1",
                                auth=(settings.HTTP_SHELLY_USERNAME, settings.HTTP_SHELLY_PASSWORD), timeout=10)
        if response.status_code == 200:
            status_json = json.loads(response.text.strip())
            if "status" in status_json and status_json["status"].upper() == "UPDATING":
                shelly.last_status = current_dt + ": Update via HTTP running"
            else:
                shelly.last_status = current_dt + ": Update via HTTP Initialized"
            print(
                "HTTP LOG - " + str(datetime.now()) + ": HTTP OK - " + response.url + " - " + str(response.status_code))
            return True
        else:
            shelly.last_status = current_dt + ": Update via HTTP failed (Response " + str(response.status_code) + ")"
            print("HTTP LOG - " + str(datetime.now()) + ": HTTP Error - " + response.url + " - " + str(
                response.status_code))
    except requests.exceptions.RequestException as e:
        shelly.last_status = current_dt + ": Exception " + str(e)
        print("HTTP LOG - " + str(datetime.now()) + ": HTTP Exception - " + str(e))

    return False


def apply_shelly_settings(shelly=None):
    """
    Apply new settings to the Shelly
    :param shelly:
    :return:
    """

    if shelly:
        shellyupdates = ShellySettingUpdates.objects.filter(shelly_id=shelly, shelly_settings_applied=False,
                                                            shelly_settings_delete=False).select_related('shelly_id').order_by('insert_ts')

    for update in shellyupdates:
        cancel = False
        try:
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            response = requests.post("http://" + update.shelly_id.shelly_ip + update.shelly_settings_path,
                                    auth=(settings.HTTP_SHELLY_USERNAME, settings.HTTP_SHELLY_PASSWORD),
                                    timeout=3,
                                    data=json.loads(update.shelly_settings_json),
                                    headers=headers)
            if response.status_code == 200:
                update.last_status_ts = datetime.now()
                update.last_status = json.loads(response.text.strip())
                update.last_status_code = response.status_code
                update.shelly_settings_applied = True
                print(
                    "HTTP LOG - " + str(datetime.now()) + ": HTTP OK - " + response.url + " - " + str(
                        response.status_code))
            else:
                update.last_status_ts = datetime.now()
                update.last_status = json.loads(response.text.strip())
                update.last_status_code = response.status_code
                print("HTTP LOG - " + str(datetime.now()) + ": HTTP Error - " + response.url + " - " + str(
                    response.status_code))
        except requests.exceptions.RequestException as e:
            update.last_status_ts = datetime.now()
            update.last_status = "HTTP Exception " + str(e)
            update.last_status_code = "FAILED"
            print("HTTP LOG - " + str(datetime.now()) + ": HTTP Exception - " + str(e))
            cancel = True

        update.save()
        if cancel:
            break
