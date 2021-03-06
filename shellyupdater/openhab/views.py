# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView
from updates.models import OpenHabThings
from .openhab_handler import get_openhab_things, join_shelly_things


class OpenhabThingsView(TemplateView):
    """
    Show all Openhab Things in a Table with the mapped Shelly
    """

    template_name = 'things_overview.html'

    def get(self, request, refresh=None, *args, **kwargs):
        """
        """

        context = {}

        # refresh starts a new http call to Openhab
        if refresh == 'Y':
            get_openhab_things()
            join_shelly_things()

        things = OpenHabThings.objects.all()
        context["things"] = things

        return self.render_to_response(context)
