default_app_config = 'updates.apps.UpdatesConfig'

from django.conf import settings
from updates.apps import start_MQTT
if settings.STARTS_WITH_GUNICORN:
    start_MQTT()