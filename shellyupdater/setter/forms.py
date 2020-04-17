import json

from django import forms
from jsonpath_ng import parse
from updates.models import MasterDataShellySettingsMatrix, Shellies, MasterDataShellySettings, ShellySettings


class SettingsWizardForm(forms.Form):

    TYPE_CHOICES = (('', '-- please select --'),) + MasterDataShellySettingsMatrix.SHELLY_DEVICES

    shelly_types = forms.ChoiceField(choices=TYPE_CHOICES, label="Shelly Type")
    shelly = forms.MultipleChoiceField(choices=[],
        label="Shellies",
        widget=forms.SelectMultiple)
    shelly_settings_topic = forms.ChoiceField(choices=MasterDataShellySettings.SETTINGS_TYPE_CHOICES,
        label="Setting")


class SettingsValuesForm(forms.Form):

    def __init__(self, request=None, shelly_type=None, settings_type=None, shellies=None, *args, **kwargs):
        super(SettingsValuesForm, self).__init__(*args, **kwargs)
        if shellies and shelly_type and settings_type:
            # Count Shellies
            shelly_cnt = len(shellies)

            # Load Settings Fields
            settings = MasterDataShellySettings.objects.filter(settingsmatrix__md_setmatrix_shellytype=shelly_type, md_settings_type=settings_type)

            # Load (reference) Shelly settings
            reference_shelly = ShellySettings.objects.get(shelly_id__id=shellies[0])
            reference_settings = json.loads(reference_shelly.shelly_settings_json)

            for set in settings:
                fieldname = set.md_settings_path + "-" + set.md_settings_parameter
                if set.md_settings_parameter_type == 'bool':
                    self.fields[fieldname] = forms.BooleanField(label='%s' % set.md_settings_parameter)
                elif set.md_settings_parameter_type == 'number':
                    self.fields[fieldname] = forms.IntegerField(label='%s' % set.md_settings_parameter)
                else:
                    self.fields[fieldname] = forms.CharField(label='%s' % set.md_settings_parameter, max_length=200)
                if set.md_settings_single and shelly_cnt and shelly_cnt > 1:
                    self.fields[fieldname].disabled=True

                self.fields[fieldname].help_text = set.md_settings_description
                self.fields[fieldname].required = False
                if request:
                    self.fields[fieldname].initial = request.get(fieldname)

                reference_settings_path = set.md_settings_reference_path

                if reference_settings_path:
                    json_path = parse('$.' + reference_settings_path)
                    matches = json_path.find(reference_settings)
                    placeholder = ""
                    if matches:
                        if set.md_settings_parameter_type == 'bool':
                            self.fields[fieldname].initial = matches[0].value
                        else:
                            placeholder = matches[0].value

                    self.fields[fieldname].widget.attrs.update({
                            'placeholder': placeholder
                    })

    def clean(self):
        return self.cleaned_data

    def is_valid(self):
        return True


class SettingsPreviewForm(forms.Form):

    def __init__(self, request=None, settings_path=None, settings_json=None, settings_encode=None, *args, **kwargs):
        super(SettingsPreviewForm, self).__init__(*args, **kwargs)
        self.fields['settings_path'] = forms.CharField(max_length=100, label="Settings path",
                                                       widget=forms.TextInput(attrs={"readonly": "readonly"}))
        self.fields['settings_json'] = forms.CharField(label="Settings to be applied", widget=forms.Textarea(
            attrs={"rows": 15, "cols": 100, "readonly": "readonly"}))
        self.fields['settings_approval'] = forms.BooleanField(
            label="I am sure to apply these settings to the above listed Shellies. I know that wrong settings can cause unusability of the shelly!")
        self.fields['settings_encode'] = forms.CharField(widget=forms.HiddenInput)

        if request:
            self.fields['settings_path'].initial = request.get('settings_path')
            self.fields['settings_json'].initial = request.get('settings_json')
            self.fields['settings_encode'].initial = request.get('settings_encode')
            self.fields['settings_approval'].initial = request.get('settings_approval')
        elif settings_path and settings_json and settings_encode:
            self.fields['settings_path'].initial = settings_path
            self.fields['settings_json'].initial = json.dumps(settings_json, indent=2)
            self.fields['settings_encode'].initial = settings_encode

    def clean(self):
        return self.cleaned_data

    def is_valid(self):
        return True