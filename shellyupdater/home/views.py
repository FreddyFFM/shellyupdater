# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.views.generic import TemplateView
from updates.models import Shellies
from django.db.models import Avg, Max, Min, Count


class HomeView(TemplateView):

    template_name = 'home.html'

    def get(self, request, refresh=None, *args, **kwargs):
        context = {}

        shelly_info = Shellies.objects.all().aggregate(Count('shelly_id'),
                                                            Max('shelly2infos__shelly_battery_percent'),
                                                            Min('shelly2infos__shelly_battery_percent'),
                                                            Avg('shelly2infos__shelly_battery_percent'),
                                                         )
        context["shelly_info"] = shelly_info

        shelly_oldest = Shellies.objects.earliest('last_change_ts')
        context["shelly_oldest"] = shelly_oldest

        if 'openhab' in settings.INSTALLED_APPS:
            from updates.models import OpenHabThings
            shellies_wo_things = Shellies.objects.filter(shelly2thing__thing_uid__isnull=True)
            things_wo_shelly = OpenHabThings.objects.filter(shelly_id__isnull=True)
            context["shellies_wo_things"] = shellies_wo_things
            context["things_wo_shelly"] = things_wo_shelly

        return self.render_to_response(context)