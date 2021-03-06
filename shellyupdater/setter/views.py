# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.shortcuts import redirect
from django.views.generic import TemplateView

from updates.models import Shellies, ShellySettingUpdates, OpenHabThings
from updates.shelly_http_handler import apply_shelly_settings
from .forms import SettingsWizardForm, SettingsValuesForm, SettingsPreviewForm
from django.http import HttpResponse


def get_shellies(request, shelly_type=None):
    """
    Provide Shellies for a Shelly-Type
    This is for the Ajax call within the form
    :param request: AJAX request
    :param shelly_type: Shelly-Type from form
    :return:
    """

    if shelly_type:
        shellies = Shellies.objects.filter(shelly_type=shelly_type).order_by('shelly_type', 'shelly_id').values('id',
                                                                                                         'shelly_id')

        for shelly in shellies:
            things = OpenHabThings.objects.filter(shelly_id__shelly_id=shelly['shelly_id'])
            if things:
                shelly['shelly_id'] = shelly['shelly_id'] + " (" + things[0].thing_label + ")"

        shelly_choices = list(shellies)

        return HttpResponse(status=200, content=json.dumps(shelly_choices), content_type='application/json')
    return HttpResponse(status=400)


class ShellyWizardSelectView(TemplateView):
    """
    View for the first page of the Shelly Settings wizard
    Select Shelly Type, Shellies and settings area
    For switching between the wizard-pages data will be stored in a session
    """

    template_name = 'shelly_settings_wizard_select.html'

    def get(self, request, *args, **kwargs):
        """
        GET view with pre-filled form
        """

        context = {}

        wizardPost = request.session.get('wizardPost')

        wizard_form = SettingsWizardForm(wizardPost)
        # Set Shellies to select based on the Shelly Type
        if wizardPost and "shelly_types" in wizardPost:
            shelly_type = wizardPost['shelly_types']
            shelly_choices = []
            shellies = Shellies.objects.filter(shelly_type=shelly_type).order_by('shelly_type',
                                                                                        'shelly_id').values('id',
                                                                                                            'shelly_id')
            for shelly in shellies:
                if OpenHabThings.objects.filter(shelly_id__shelly_id=shelly['shelly_id']).exists():
                    thing = OpenHabThings.objects.filter(shelly_id__shelly_id=shelly['shelly_id'])[0]
                    shelly_id = shelly['shelly_id'] + " (" + thing.thing_label + ")"
                else:
                    shelly_id = shelly['shelly_id']
                shelly_choices.append((shelly['id'], shelly_id))


            wizard_form.fields['shelly'].choices = shelly_choices

        context["wizard_form"] = wizard_form

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """
        POST view with prefilled form based on POST request
        """

        context = {}

        request.session['wizardPost'] = request.POST

        wizard_form = SettingsWizardForm(request.POST)
        # Set Shellies to select based on the Shelly Type
        if wizard_form.data['shelly_types']:
            shelly_type = wizard_form.data['shelly_types']
            shelly_choices = [(shelly['id'], shelly['shelly_id']) for shelly in
                              Shellies.objects.filter(shelly_type=shelly_type).order_by('shelly_type',
                                                                                        'shelly_id').values('id',
                                                                                                            'shelly_id')]
            wizard_form.fields['shelly'].choices = shelly_choices

        if wizard_form.is_valid():
            request.session['shelly_type'] = wizard_form.cleaned_data['shelly_types']
            request.session['shelly'] = wizard_form.cleaned_data['shelly']
            request.session['shelly_settings_topic'] = wizard_form.cleaned_data['shelly_settings_topic']
            try:
                del request.session['valuesPost']
            except KeyError:
                pass
            return redirect(to='settings/set')
        context["wizard_form"] = wizard_form

        return self.render_to_response(context)


class ShellyWizardValuesView(TemplateView):
    """
    View for the second page of the wizard
    Form to enter the Shelly type specific values
    """

    template_name = 'shelly_settings_wizard_values.html'

    def get(self, request, *args, **kwargs):
        """
        Get View
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        context = {}

        valuesPost = request.session.get('valuesPost')

        shelly_type = request.session.get('shelly_type')
        settings_type = request.session.get('shelly_settings_topic')
        shelly = request.session.get('shelly')

        settings_form = SettingsValuesForm(request=valuesPost,
                                           shelly_type=shelly_type,
                                           settings_type=settings_type,
                                           shellies=shelly)
        context["settings_form"] = settings_form

        shellies = Shellies.objects.filter(id__in=shelly)
        context["shelly_type"] = shelly_type
        context["shellies"] = shellies
        context["settings_type"] = settings_type

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """
        Post view
        """

        context = {}

        shelly_type = request.session.get('shelly_type')
        settings_type = request.session.get('shelly_settings_topic')
        shelly = request.session.get('shelly')

        settings_form = SettingsValuesForm(request.POST,
                                           shelly_type=shelly_type,
                                           settings_type=settings_type,
                                           shellies=shelly
                                           )

        if settings_form.is_valid():
            request.session['valuesPost'] = settings_form.cleaned_data
            return redirect(to='settings/preview')

        context["settings_form"] = settings_form

        shellies = Shellies.objects.filter(id__in=shelly)
        context["shelly_type"] = shelly_type
        context["shellies"] = shellies
        context["settings_type"] = settings_type

        return self.render_to_response(context)


class ShellyWizardPreviewView(TemplateView):
    """
    Final view for the wizard to review the settings before application
    """

    template_name = 'shelly_settings_wizard_preview.html'

    def get(self, request, *args, **kwargs):
        """
        Get view
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        context = {}

        shelly_type = request.session.get('shelly_type')
        settings_type = request.session.get('shelly_settings_topic')
        shelly = request.session.get('shelly')

        values = request.session.get('valuesPost')
        settings_json = {}
        settings_encode = ""
        path = ""
        for key, value in values.items():
            if key.startswith('/'):
                param = key.split('-')[1]
                path = key.split('-')[0]
                type = key.split('-')[2]
                if value or value == 0 or type == "bool":
                    if type == "number":
                        settings_json[param] = value
                    else:
                        settings_json[param] = str(value)
                    settings_encode = param + "=" + str(value) + "\n" + settings_encode

        preview_form = SettingsPreviewForm(settings_path=path, settings_json=settings_json, settings_encode=settings_encode)

        context["preview_form"] = preview_form

        shellies = Shellies.objects.filter(id__in=shelly)
        context["shelly_type"] = shelly_type
        context["shellies"] = shellies
        context["settings_type"] = settings_type

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """
        Post view
        """

        context = {}

        shelly_type = request.session.get('shelly_type')
        settings_type = request.session.get('shelly_settings_topic')
        shelly = request.session.get('shelly')

        settings_path = request.POST.get('settings_path')
        settings_json = request.POST.get('settings_json')
        settings_encode = request.POST.get('settings_encode')

        shellies = Shellies.objects.filter(id__in=shelly)

        if settings_path and settings_json and settings_encode:
            ids = []
            for shelly in shellies:
                settings_update = ShellySettingUpdates(shelly_id=shelly)
                settings_update.shelly_settings_path = settings_path
                settings_update.shelly_settings_json = settings_json
                settings_update.shelly_settings_encoded = settings_encode
                settings_update.last_status = "Inserted"
                settings_update.save()
                ids.append(settings_update.id)

                apply_shelly_settings(shelly=shelly)

            update_status = ShellySettingUpdates.objects.filter(id__in=ids)

            context["update_status"] = update_status
            context["success"] = True

        else:
            context["success"] = False

        context["shellies"] = shellies
        context["shelly_type"] = shelly_type
        context["settings_type"] = settings_type

        return self.render_to_response(context)


class SettingsView(TemplateView):
    """
    Overview of all Settings made
    """

    template_name = 'settings_overview.html'

    def get(self, request, *args, **kwargs):

        context = {}

        setting_updates = ShellySettingUpdates.objects.all()
        context["setting_updates"] = setting_updates

        return self.render_to_response(context)
