"""
This handler covers all functionality in communication with Openhab
"""

import requests
import re
import logging

from datetime import datetime
from django.conf import settings
from updates.models import Shellies, OpenHabThings


logger = logging.getLogger(__name__)


def put_thing(uid=None, label="", location=""):
    """
    Save an Openhab Thing to DB
    :param uid:
    :param label:
    :param location:
    :return:
    """
    if uid:
        # If not exists (UID) create a new one
        if OpenHabThings.objects.filter(thing_uid=uid).exists():
            thing = OpenHabThings.objects.get(thing_uid=uid)
        else:
            thing = OpenHabThings()
            thing.thing_uid = uid

        if label:
            thing.thing_label = label
        else:
            thing.thing_label = 'N/A'

        if location:
            thing.thing_location = location
        else:
            thing.thing_location = 'N/A'

        thing.save()


def get_openhab_things():
    """
    Get all MQTT Shelly Openhab Things via HTPP request against Openhab REST API
    Only Things starting with mqtt:topic:shellies are considered
    :return:
    """
    try:
        response = requests.get(settings.OPENHAB_REST_BASE_URL + "/things")
        if response.status_code == 200:
            things = response.json()
            for thing in things:
                if thing["thingTypeUID"] == "mqtt:topic" and thing["UID"].startswith("mqtt:topic:shellies"):
                    if "label" in thing:
                        label = thing["label"]
                    if "location" in thing:
                        location = thing["location"]

                    put_thing(uid=thing["UID"], label=label, location=location)
            logger.info(
                "HTTP LOG - " + str(datetime.now()) + ": HTTP OK - " + response.url + " - " + str(response.status_code))
        else:
            logger.error(
                "HTTP LOG - " + str(datetime.now()) + ": HTTP Error - " + response.url + " - " + str(response.status_code))
    except requests.exceptions.RequestException as e:
        logger.error("HTTP LOG - " + str(datetime.now()) + ": HTTP Exception - " + str(e))
    except Exception as e:
        logger.error("HTTP LOG - " + str(datetime.now()) + ": Other Exception - " + str(e))



def join_shelly_things():
    """
    Join Openhab Things to Shelly based on the shelly-id
    :return:
    """
    things = OpenHabThings.objects.all()
    for thing in things:
        # Split the Thing ID and retrieve Shelly-ID (is the 4th part)
        # Thing mqtt:topic:shellies:shellyswitch25-xxxxxx -> shellyswitch25-xxxxxx
        # Thing mqtt:topic:shellies:shellyplug-s-xxxxxx -> shellyplug-s-xxxxxx
        # Thing mqtt:topic:shellies:shellyswitch25-xxxxxx-HE-KE -> shellyswitch25-xxxxxx
        # thing_shelly_id = (thing.thing_uid.split(":")[3]).split("-", maxsplit=1)
        # thing_shelly_id = thing_shelly_id[0] + "-" + thing_shelly_id[1].split("-")[0]
        re_pattern = "(shelly[\w]+)(\-s)?\-([\w]+)\-?.*"
        re_matches = re.match(re_pattern, thing.thing_uid.split(":")[3])
        thing_shelly_id = re_matches.group(1) + (re_matches.group(2) if re_matches.group(2) else "") + "-" + re_matches.group(3)

        # If Shelly-ID exists than map to Thing
        if Shellies.objects.filter(shelly_id=thing_shelly_id).exists():
            shelly = Shellies.objects.get(shelly_id=thing_shelly_id)
            thing.shelly_id = shelly
        else:
            thing.shelly_id = None
        thing.save()


