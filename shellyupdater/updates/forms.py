"""
This module handles all forms for the Shelly Overview and Details pages
"""

from django import forms

from updates.models import Shellies


class ShellySelectForm(forms.ModelForm):
    """
    SelectForm for selecting a Shelly in the Details View
    """

    shelly = forms.ModelChoiceField(queryset=Shellies.objects.all().order_by('shelly_id'), to_field_name='shelly_id')

    def __init__(self, *args, **kwargs):
        self.shelly_id = kwargs.pop('shelly_id', None)
        super(ShellySelectForm, self).__init__(*args, **kwargs)
        if self.shelly_id:
            self.fields['shelly'].initial = self.shelly_id

    class Meta:
        model = Shellies

        fields = ['shelly']

        labels = {
            'shelly': 'Shelly'
        }

        widgets = {
            'shelly': forms.TextInput(
                attrs={'class': 'form-control'})
        }
