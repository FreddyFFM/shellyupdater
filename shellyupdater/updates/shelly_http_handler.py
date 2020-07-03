"""
This module handles the http communication to the Shellies
"""

import requests
import json
import logging

from datetime import datetime
from django.conf import settings
from .models import Shellies, ShellySettings, ShellySettingUpdates

logger = logging.getLogger(__name__)


def http_get(url, timeout=3):
    try:
        req_session = requests.Session()
        response = req_session.get(url,
                                   auth=(settings.HTTP_SHELLY_USERNAME, settings.HTTP_SHELLY_PASSWORD), timeout=timeout)
        logger.debug(
            "HTTP LOG - " + str(datetime.now()) + ": HTTP OK Request Headers - " + response.url + " - " + str(
                response.request.headers))
        if response.status_code == 200:
            logger.info(
                "HTTP LOG - " + str(datetime.now()) + ": HTTP OK - " + response.url + " - " + str(response.status_code))
            logger.debug(
                "HTTP LOG - " + str(datetime.now()) + ": HTTP OK Response - " + response.url + " - " + str(
                    response.text.strip()))
            logger.debug(
                "HTTP LOG - " + str(datetime.now()) + ": HTTP OK Headers - " + response.url + " - " + str(
                    response.headers))
        else:
            logger.error("HTTP LOG - " + str(datetime.now()) + ": HTTP Error - " + response.url + " - " + str(
                response.status_code))
            logger.error(
                "HTTP LOG - " + str(datetime.now()) + ": HTTP Error - " + response.url + " - " + str(
                    response.text.strip()))

        return_resp = {"response": response}

    except requests.Timeout as e:
        return_resp = {"exception": e}
        logger.error("HTTP LOG - " + str(datetime.now()) + ": HTTP Timeout - " + str(e))
        pass
    except requests.ConnectionError as e:
        return_resp = {"exception": e}
        logger.error("HTTP LOG - " + str(datetime.now()) + ": HTTP Connection - " + str(e))
        pass
    except requests.exceptions.RequestException as e:
        return_resp = {"exception": e}
        logger.error("HTTP LOG - " + str(datetime.now()) + ": HTTP Exception - " + str(e))
        pass
    except Exception as e:
        return_resp = {"exception": e}
        logger.error("HTTP LOG - " + str(datetime.now()) + ": Other Exception - " + str(e))
        pass

    return return_resp


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

    if get_shelly_settings(shelly=shelly, shellySettings=shellySettings) and get_shelly_status(shelly=shelly,
                                                                                               shellySettings=shellySettings):
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
    resp = http_get("http://" + shelly.shelly_ip + "/settings")
    if "response" in resp:
        response = resp["response"]
        if response.status_code == 200:
            try:
                shellySettings.shelly_settings_json = json.dumps(json.loads(response.text.strip()), indent=4,
                                                                 sort_keys=True)
                status = current_dt + ": HTTP OK " + str(response.status_code)
            except Exception as e:
                logger.error(
                    "SHELLY LOG - " + str(datetime.now()) + ": GET SETTINGS Exception: " + str(e))
                shelly.last_status = current_dt + ": Settings Exception: " + str(e)
        else:
            status = current_dt + ": HTTP Error " + str(response.status_code)
    else:
        exception = resp["exception"]
        status = current_dt + ": Exception " + str(exception)

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
    resp = http_get("http://" + shelly.shelly_ip + "/status")
    if "response" in resp:
        response = resp["response"]
        if response.status_code == 200:
            try:
                status_json = json.loads(response.text.strip())
                shellySettings.shelly_status_json = json.dumps(status_json, indent=4, sort_keys=True)
                if "bat" in status_json:
                    shellySettings.shelly_battery_percent = status_json["bat"]["value"]
                    shellySettings.shelly_battery_voltage = status_json["bat"]["voltage"]
                if "wifi_sta" in status_json:
                    shellySettings.shelly_wifi_ssid = status_json["wifi_sta"]["ssid"]
                    shellySettings.shelly_wifi_strength = status_json["wifi_sta"]["rssi"]
                if "update" in status_json:
                    shelly.shelly_fw_version_new = status_json["update"]["new_version"]
                status = current_dt + ": HTTP OK " + str(response.status_code)
            except Exception as e:
                logger.error(
                    "SHELLY LOG - " + str(datetime.now()) + ": GET STATUS Exception: " + str(e))
                shelly.last_status = current_dt + ": Status Exception: " + str(e)
        else:
            status = current_dt + ": HTTP Error " + str(response.status_code)
    else:
        exception = resp["exception"]
        status = current_dt + ": Exception " + str(exception)

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
    resp = http_get("http://" + shelly.shelly_ip + "/ota?update=1")
    if "response" in resp:
        response = resp["response"]
        if response.status_code == 200:
            try:
                status_json = json.loads(response.text.strip())
                if "status" in status_json and status_json["status"].upper() == "UPDATING":
                    shelly.last_status = current_dt + ": Update via HTTP running"
                else:
                    shelly.last_status = current_dt + ": Update via HTTP Initialized"
                return True
            except Exception as e:
                logger.error(
                    "SHELLY LOG - " + str(datetime.now()) + ": PERFORM UPDATE Exception: " + str(e))
                shelly.last_status = current_dt + ": Update Exception: " + str(e)
        else:
            shelly.last_status = current_dt + ": Update via HTTP failed (Response " + str(response.status_code) + ")"
    else:
        exception = resp["exception"]
        shelly.last_status = current_dt + ": Exception " + str(exception)

    return False


def apply_shelly_settings(shelly=None):
    """
    Apply new settings to the Shelly
    :param shelly:
    :return:
    """

    shellyupdates = None
    if shelly:
        shellyupdates = ShellySettingUpdates.objects.filter(shelly_id=shelly, shelly_settings_applied=False,
                                                            shelly_settings_delete=False).select_related(
            'shelly_id').order_by('insert_ts')

    if shellyupdates:
        logger.info(
            "SHELLY LOG - " + str(datetime.now()) + ": SHELLY APPLY NEW SETTINGS - ID: " + str(shelly))

    for update in shellyupdates:
        cancel = False
        try:
            req_session = requests.Session()
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            response = req_session.post("http://" + update.shelly_id.shelly_ip + update.shelly_settings_path,
                                     auth=(settings.HTTP_SHELLY_USERNAME, settings.HTTP_SHELLY_PASSWORD),
                                     timeout=3,
                                     data=update.shelly_settings_encoded,
                                     headers=headers)
            logger.debug(
                "HTTP LOG - " + str(datetime.now()) + ": HTTP OK Request Headers - " + response.url + " - " + str(
                    response.request.headers))
            logger.debug(
                "HTTP LOG - " + str(datetime.now()) + ": HTTP OK Request Body - " + response.url + " - " + str(
                    response.request.body))

            if response.status_code == 200:
                update.last_status_ts = datetime.now()
                update.last_status = response.text.strip()
                update.last_status_code = response.status_code
                update.shelly_settings_applied = True
                logger.info(
                    "HTTP LOG - " + str(datetime.now()) + ": HTTP OK - " + response.url + " - " + str(
                        response.status_code))
                logger.debug(
                    "HTTP LOG - " + str(datetime.now()) + ": HTTP OK Response - " + response.url + " - " + str(
                        response.text.strip()))
                logger.debug(
                    "HTTP LOG - " + str(datetime.now()) + ": HTTP OK Headers - " + response.url + " - " + str(
                        response.headers))
            else:
                update.last_status_ts = datetime.now()
                update.last_status = response.text.strip()
                update.last_status_code = response.status_code
                logger.error("HTTP LOG - " + str(datetime.now()) + ": HTTP Error - " + response.url + " - " + str(
                    response.status_code))
                logger.error(
                    "HTTP LOG - " + str(datetime.now()) + ": HTTP Error - " + response.url + " - " + str(
                        response.text.strip()))
        except requests.Timeout as e:
            update.last_status_ts = datetime.now()
            update.last_status = "HTTP Timeout " + str(e)
            update.last_status_code = "TIMEOUT"
            cancel = True
            logger.error("HTTP LOG - " + str(datetime.now()) + ": HTTP Timeout - " + str(e))
            pass
        except requests.ConnectionError as e:
            update.last_status_ts = datetime.now()
            update.last_status = "HTTP ConnectionError " + str(e)
            update.last_status_code = "CONNECTION ERROR"
            cancel = True
            logger.error("HTTP LOG - " + str(datetime.now()) + ": HTTP ConnectionError - " + str(e))
            pass
        except requests.exceptions.RequestException as e:
            update.last_status_ts = datetime.now()
            update.last_status = "HTTP Exception " + str(e)
            update.last_status_code = "FAILED"
            cancel = True
            logger.error("HTTP LOG - " + str(datetime.now()) + ": HTTP Exception - " + str(e))
            pass
        except Exception as e:
            update.last_status_ts = datetime.now()
            update.last_status = "Other Exception " + str(e)
            update.last_status_code = "OTHER"
            cancel = True
            logger.error("HTTP LOG - " + str(datetime.now()) + ": Other Exception - " + str(e))
            pass

        update.save()
        if cancel:
            break
