# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time

from django.views.generic import TemplateView
from django.conf import settings
from updates.models import Shellies, ShellySettings
from datetime import datetime
from shellyupdater.mqtt import get_mqttclient
from .shelly_http_handler import get_shelly_info
from django.http import HttpResponse


class ShowShelliesView(TemplateView):

    template_name = 'shellies_overview.html'

    def get(self, request, refresh=None, *args, **kwargs):
        """
        """

        context = {}

        if refresh == 'Y':
            mqttclient = get_mqttclient()
            if mqttclient.is_connected():

                i = 1
                while True:
                    result = mqttclient.publish(settings.MQTT_SHELLY_COMMAND_TOPIC, "announce")
                    if result.rc == 0 or i > 3:
                        break
                    i = i + 1
                    time.sleep(1)

                if result.rc == 0:
                    time.sleep(2)
                else:
                    context["error"] = True

        shellies = Shellies.objects.all()
        context["shellies"] = shellies

        return self.render_to_response(context)

    def post(self, request, at_id=None, task=None, *args, **kwargs):
        """

        """

        context = {}

        items = request.POST.items()
        current_dt = datetime.now().strftime("%d.%m.%Y %H:%M")
        for key, val in items:
            if key.upper().startswith("SHELLY") and val == "on":
                mqttclient = get_mqttclient()
                if mqttclient.is_connected():
                    shelly = Shellies.objects.get(shelly_id=key)
                    shelly.shelly_do_update = True
                    if shelly.shelly_online:
                        i = 1
                        while True:
                            result = mqttclient.publish(topic=settings.MQTT_SHELLY_BASE_TOPIC + key + "/command",
                                                        payload="update_fw", qos=1, retain=True)
                            if result.rc == 0 or i > 3:
                                break
                            i = i + 1
                            time.sleep(1)

                        if result.rc != 0:
                            shelly.last_status = current_dt + ": Update failed (" + str(result.rc) + ")"
                        else:
                            shelly.last_status = current_dt + ": Update Initialized"

                    else:
                        shelly.last_status = current_dt + ": Marked for update"

                    shelly.save()

        shellies = Shellies.objects.all()
        context["shellies"] = shellies

        return self.render_to_response(context)


class ShellyDetailView(TemplateView):

    template_name = 'shelly_details.html'

    def get(self, request, shelly_id=None, refresh=None, *args, **kwargs):
        """

        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        context = {}

        if not shelly_id:
            return HttpResponse(content="ID not found", status=400)

        if ShellySettings.objects.filter(shelly_id__shelly_id=shelly_id).exists():
            if refresh == "Y":
                get_shelly_info(shelly_id=shelly_id)
            details = ShellySettings.objects.get(shelly_id__shelly_id=shelly_id)
        else:
            if get_shelly_info(shelly_id=shelly_id):
                details = ShellySettings.objects.get(shelly_id__shelly_id=shelly_id)
            else:
                return HttpResponse(content="Error getting details", status=400)

        context["details"] = details

        return self.render_to_response(context)
