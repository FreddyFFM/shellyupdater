# shellyupdater

## What is ShellyUpdater?

As I do setup my Shelly manually via the webinterface and add them to my MQTT broker (I do not use the Shelly Cloud Services nor the app), I thaught of building up a small web-page to get more information about my shellies. Which firmware, battery status, settings, etc...
Also I searched for an option to update the non permanent online devices via MQTT. So at the end, here it is - the ShellyUpdater, based on python, django and MQTT.
Due to my integration with Openhab I also can request the MQTT Shelly Things from the Openhab-REST-API.

## How to use/install?

I did not setup everything to run immediatly after cloning the repo, but with some small steps you can run it in a docker container via docker-compose.

1. Change docker-compose.yaml (Change the volume path to your local directory structure)
2. Copy .env.example to .env and fill out the Settings.
3. Build and run the docker via docker-compose

## Notice

Please be aware that this tool was designed to interact with Openhab. If you do not use Openhab you have to comment out 'openhab' in the settings.py, section INSTALLED_APPS.


