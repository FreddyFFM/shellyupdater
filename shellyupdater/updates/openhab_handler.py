import requests

from django.conf import settings
from .models import OpenHabThings, Shellies

def put_thing(uid=None, label="", location=""):
    if uid:
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


def join_shelly_things():

    things = OpenHabThings.objects.all()
    for thing in things:
        thing_shelly_id = (thing.thing_uid.split(":")[3]).split("-", maxsplit=1)
        thing_shelly_id = thing_shelly_id[0] + "-" + thing_shelly_id[1].split("-")[0]

        if Shellies.objects.filter(shelly_id=thing_shelly_id).exists():
            shelly = Shellies.objects.get(shelly_id=thing_shelly_id)

        thing.shelly_id = shelly
        thing.save()


