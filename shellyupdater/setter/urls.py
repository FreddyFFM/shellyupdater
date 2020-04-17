from .views import ShellyWizardSelectView, ShellyWizardValuesView, get_shellies, ShellyWizardPreviewView
from django.urls import path, re_path

urlpatterns = [
    path('', ShellyWizardSelectView.as_view(), name="settings"),
    path('set/', ShellyWizardValuesView.as_view(), name="settings/set"),
    path('preview/', ShellyWizardPreviewView.as_view(), name="settings/preview"),

    re_path('^shellies/(?P<shelly_type>[A-Z0-9]+)/$', get_shellies, name="settings/shellies"),
]
