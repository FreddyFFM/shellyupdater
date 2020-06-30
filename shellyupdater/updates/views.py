# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time
import logging

from django.views.generic import TemplateView
from django.conf import settings
from updates.models import Shellies, ShellySettings, ShellySettingUpdates
from datetime import datetime
from shellyupdater.mqtt import get_mqttclient
from .forms import ShellySelectForm
from .shelly_http_handler import get_shelly_info, perform_update_http


logger = logging.getLogger(__name__)


class ShowShelliesView(TemplateView):
    """
    Provide the Shelly overview
    """

    template_name = 'shellies_overview.html'

    def get(self, request, refresh=None, *args, **kwargs):
        """
        Show table with all Shelly and their information
        """

        context = {}

        # If refresh initiate a refresh via MQTT
        if refresh == 'Y':
            logger.info(
                "SHELLY LOG - " + str(datetime.now()) + ": SHELLY MASS ANNOUNCE")

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
        This is executed is Shellies are marked for updates
        """

        context = {}

        items = request.POST.items()
        current_dt = datetime.now().strftime("%d.%m.%Y %H:%M")
        # for every Shelly marked start the update (if online) else mark the shelly for update
        # when comming online
        for key, val in items:
            if key.upper().startswith("SHELLY") and val == "on":
                shelly = Shellies.objects.get(shelly_id=key)
                shelly.shelly_fw_version_old = shelly.shelly_fw_version
                shelly.shelly_do_update = True
                if shelly.shelly_online:
                    logger.info(
                        "SHELLY LOG - " + str(datetime.now()) + ": SHELLY PERFORM UPDATE - ID: " + str(id))
                    perform_update_http(shelly=shelly)
                else:
                    shelly.last_status = current_dt + ": Marked for update"

                shelly.save()

        shellies = Shellies.objects.all()
        context["shellies"] = shellies

        return self.render_to_response(context)


class ShellyDetailView(TemplateView):
    """
    Provide the Shelly Detail view
    (Current settings, status and the already apllied new settings and their status)
    """

    template_name = 'shelly_details.html'

    def get(self, request, shelly_id=None, refresh=None, *args, **kwargs):
        """
        Get view
        if called with refresh an http request will be send to the Shelly updating current settings and status
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        context = {}

        shelly_select_form = ShellySelectForm(shelly_id=shelly_id)
        context["shelly_select_form"] = shelly_select_form

        if shelly_id:
            details = None
            if ShellySettings.objects.filter(shelly_id__shelly_id=shelly_id).exists():
                if refresh == "Y":
                    logger.info(
                        "SHELLY LOG - " + str(datetime.now()) + ": SHELLY CATCH INFOS - ID: " + str(shelly_id))
                    get_shelly_info(shelly_id=shelly_id)
                details = ShellySettings.objects.get(shelly_id__shelly_id=shelly_id)
            else:
                logger.info(
                    "SHELLY LOG - " + str(datetime.now()) + ": SHELLY CATCH INFOS - ID: " + str(shelly_id))
                if get_shelly_info(shelly_id=shelly_id):
                    details = ShellySettings.objects.get(shelly_id__shelly_id=shelly_id)

            update_status = ShellySettingUpdates.objects.filter(shelly_id__shelly_id=shelly_id)

            context["details"] = details
            context["update_status"] = update_status

        return self.render_to_response(context)
