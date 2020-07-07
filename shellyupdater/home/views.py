# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.conf import settings
from django.views.generic import TemplateView
from datetime import datetime
from shellyupdater.mqtt import get_mqttclient
from updates.models import Shellies
from django.db.models import Avg, Max, Min, Count


logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    """
    Providing the Home-Overview
    """

    template_name = 'home.html'

    def get(self, request, refresh=None, *args, **kwargs):
        context = {}

        # Check for MQTT Connection
        mqttclient = get_mqttclient()
        if not (mqttclient and mqttclient.is_connected()):
            context["mqtt_error"] = True

        try:
            # Get Summary about Shellies and battery status
            shelly_info = Shellies.objects.all().aggregate(Count('shelly_id'),
                                                                Max('shelly2infos__shelly_battery_percent'),
                                                                Min('shelly2infos__shelly_battery_percent'),
                                                                Avg('shelly2infos__shelly_battery_percent'),
                                                             )
            context["shelly_info"] = shelly_info

            # Get Shelly with lowest battery
            if Shellies.objects.filter(shelly2infos__shelly_battery_percent__isnull=False).order_by('shelly2infos__shelly_battery_percent').exists():
                shelly_min_battery = Shellies.objects.filter(shelly2infos__shelly_battery_percent__isnull=False).order_by('shelly2infos__shelly_battery_percent')[0]
                context["shelly_min_battery"] = shelly_min_battery

            # Get Shelly longest NOT online
            shelly_oldest = Shellies.objects.earliest('last_change_ts')
            context["shelly_oldest"] = shelly_oldest

            # If Openhab Modul is activated get summary about Shelly-Openhab-link
            if 'openhab' in settings.INSTALLED_APPS:
                from updates.models import OpenHabThings
                shellies_wo_things = Shellies.objects.filter(shelly2thing__thing_uid__isnull=True)
                things_wo_shelly = OpenHabThings.objects.filter(shelly_id__isnull=True)
                context["shellies_wo_things"] = shellies_wo_things
                context["things_wo_shelly"] = things_wo_shelly

        except Exception as e:
            logger.error(
                "DB LOG - " + str(datetime.now()) + ": Database Exception - " + str(e))
            pass

        return self.render_to_response(context)