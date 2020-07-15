"""
This module handles all forms for the Shelly-Settings-Wizard
"""

import json

from django import forms
from jsonpath_ng import parse
from updates.models import MasterDataShellySettingsMatrix, MasterDataShellySettings, ShellySettings


class SettingsWizardForm(forms.Form):
    """
    Wizard-Page 1
    Select Shelly-Type and one or more Shelly the settings will apply to as well as the settings area
    """

    TYPE_CHOICES = (('', '-- please select --'),) + MasterDataShellySettingsMatrix.SHELLY_DEVICES

    shelly_types = forms.ChoiceField(choices=TYPE_CHOICES, label="Shelly Type")
    shelly = forms.MultipleChoiceField(choices=[],
        label="Shellies",
        widget=forms.SelectMultiple)
    shelly_settings_topic = forms.ChoiceField(choices=MasterDataShellySettings.SETTINGS_TYPE_CHOICES,
        label="Setting")


class SettingsValuesForm(forms.Form):
    """
    Build a dynamic form for the available settings for the selected Shelly-Type
    """

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.shelly_type = kwargs.pop('shelly_type', None)
        self.settings_type = kwargs.pop('settings_type', None)
        self.shellies = kwargs.pop('shellies', None)
        super(SettingsValuesForm, self).__init__(*args, **kwargs)
        # A Shelly-Type, at least one Shelly and a settings area have to be selected
        if self.shellies and self.shelly_type and self.settings_type:
            # Count Shellies
            shelly_cnt = len(self.shellies)

            # Load Settings Fields
            settings = MasterDataShellySettings.objects.filter(settingsmatrix__md_setmatrix_shellytype=self.shelly_type,
                                                               md_settings_type=self.settings_type)

            # Load (reference) Shelly settings
            reference_settings = None
            if ShellySettings.objects.filter(shelly_id__id=self.shellies[0]).exists():
                reference_shelly = ShellySettings.objects.get(shelly_id__id=self.shellies[0])
                reference_settings = json.loads(reference_shelly.shelly_settings_json)

            # For each setting create a new Field
            for set in settings:
                # Fieldname is created by settings-path, parameter and parameter type
                fieldname = set.md_settings_path + "-" + set.md_settings_parameter + "-" + set.md_settings_parameter_type
                if set.md_settings_parameter_type == 'bool':
                    self.fields[fieldname] = forms.BooleanField(label='%s' % set.md_settings_parameter)
                elif set.md_settings_parameter_type == 'number':
                    self.fields[fieldname] = forms.IntegerField(label='%s' % set.md_settings_parameter)
                else:
                    self.fields[fieldname] = forms.CharField(label='%s' % set.md_settings_parameter, max_length=200)

                # Exclude fields which are only suitable for on Shelly selected (like IP-Address)
                if set.md_settings_single and shelly_cnt and shelly_cnt > 1:
                    self.fields[fieldname].disabled=True

                self.fields[fieldname].help_text = set.md_settings_description
                self.fields[fieldname].required = False

                reference_settings_path = set.md_settings_reference_path
                # If value is POSTed fill this value, else prefill with current value from Shelly (if exists)
                if reference_settings_path and reference_settings:
                    json_path = parse('$.' + reference_settings_path)
                    matches = json_path.find(reference_settings)
                    placeholder = ""
                    if self.request and self.request.get(fieldname, None):
                        self.fields[fieldname].initial = self.request.get(fieldname)
                    elif matches:
                        if set.md_settings_parameter_type == 'bool':
                            self.fields[fieldname].initial = matches[0].value
                        else:
                            placeholder = matches[0].value

                    self.fields[fieldname].widget.attrs.update({
                            'placeholder': placeholder
                    })


class SettingsPreviewForm(forms.Form):
    """
    Create a form with a preview of the settings to be applied
    Show the settings area, a json with the values, a hidden url_encoded field and a approval field
    """

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.settings_path = kwargs.pop('settings_path', None)
        self.settings_json = kwargs.pop('settings_json', None)
        self.settings_encode = kwargs.pop('settings_encode', None)
        super(SettingsPreviewForm, self).__init__(*args, **kwargs)
        self.fields['settings_path'] = forms.CharField(max_length=100, label="Settings path",
                                                       widget=forms.TextInput(attrs={"readonly": "readonly"}))
        self.fields['settings_json'] = forms.CharField(label="Settings to be applied", widget=forms.Textarea(
            attrs={"rows": 15, "cols": 100, "readonly": "readonly"}))
        self.fields['settings_approval'] = forms.BooleanField(
            label="I am sure to apply these settings to the above listed Shellies. I know that wrong settings can cause unusability of the shelly!")
        self.fields['settings_encode'] = forms.CharField(widget=forms.HiddenInput)

        if self.request:
            self.fields['settings_path'].initial = self.request.get('settings_path')
            self.fields['settings_json'].initial = self.request.get('settings_json')
            self.fields['settings_encode'].initial = self.request.get('settings_encode')
            self.fields['settings_approval'].initial = self.request.get('settings_approval')
        elif self.settings_path and self.settings_json and self.settings_encode:
            self.fields['settings_path'].initial = self.settings_path
            self.fields['settings_json'].initial = json.dumps(self.settings_json, indent=2)
            self.fields['settings_encode'].initial = self.settings_encode
