default_app_config = 'updates.apps.UpdatesConfig'

from django.conf import settings
from updates.apps import start_MQTT
from shellyupdater import __STARTED_MQTT__

if settings.STARTS_WITH_GUNICORN:
    if not __STARTED_MQTT__:
        start_MQTT()
        __STARTED_MQTT__ = True
