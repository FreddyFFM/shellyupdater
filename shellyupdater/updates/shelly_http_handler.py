import requests
import json

from datetime import datetime
from django.conf import settings
from .models import Shellies, ShellySettings


def get_shelly_info(shelly_id=None):
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
        return True

    return False


def get_shelly_settings(shelly=None, shellySettings=None):
    if not shelly or not shellySettings:
        return False

    current_dt = datetime.now().strftime("%d.%m.%Y %H:%M")
    try:
        response = requests.get("http://" + shelly.shelly_ip + "/settings",
                            auth=(settings.HTTP_SHELLY_USERNAME, settings.HTTP_SHELLY_PASSWORD), timeout=2)
        if response.status_code == 200:
            shellySettings.shelly_settings_json = json.dumps(json.loads(response.text.strip()), indent=4, sort_keys=True)
            status = current_dt + ": HTTP OK " + str(response.status_code)
        else:
            status = current_dt + ": HTTP Error " + str(response.status_code)
    except requests.exceptions.RequestException as e:
        status = current_dt + ": Exception " + str(e)

    shellySettings.last_status_settings = status

    return True


def get_shelly_status(shelly=None, shellySettings=None):
    if not shelly or not shellySettings:
        return False

    current_dt = datetime.now().strftime("%d.%m.%Y %H:%M")
    try:
        response = requests.get("http://" + shelly.shelly_ip + "/status",
                                auth=(settings.HTTP_SHELLY_USERNAME, settings.HTTP_SHELLY_PASSWORD), timeout=2)
        if response.status_code == 200:
            shellySettings.shelly_status_json = json.dumps(json.loads(response.text.strip()), indent=4, sort_keys=True)
            status = current_dt + ": HTTP OK " + str(response.status_code)
        else:
            status =  current_dt + ": HTTP Error " + str(response.status_code)
    except requests.exceptions.RequestException as e:
        status = current_dt + ": Exception " + str(e)

    shellySettings.last_status_status = status

    return True
