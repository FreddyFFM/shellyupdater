# ShellyUpdater

## What is ShellyUpdater?

As I do setup my Shelly manually via the htpp-interface and add them to my MQTT broker (I do not use the Shelly Cloud 
Services nor the app), I thought of building up a small web-page to get more information about my Shellies. Which 
firmware, battery status, settings, etc...
Also I searched for an option for a scheduled (mass) update of the devices devicesa, escpecially the non permanent 
online ones (like a door/window sensor). So at the end, here it is - the ShellyUpdater, written in Python and based 
on Django and MQTT.
Due to my integration with Openhab I also can request the MQTT Shelly Things from the Openhab REST API.

**Some features**

* Gives an overview on all MQTT connected Shellies with details on
    * current settings and status
    * last online timestamp and battery power
    * and a link to directly jump to the shelly-http-Interface
* Possibility to mass-update Shelly-Firmware (postponed for retry when Shelly is offline)
* Possibility to mass-update Shelly-Settings via http (postponed for retry when Shelly is offline)
    * Includes General settings (like mqtt)
    * Wifi AP, Wifi Client and Wifi Backup
    * as well as login data
* Integrates with MQTT and subscribes to the announcements and online status
* Option to integrate with Openhab (Overview on Shelly-Things) via the Openhab REST API


## How to use/install?

I did not setup everything to run immediately after cloning the repo, but with some small steps you can run it in a docker container via docker-compose.

1. Change docker-compose.yaml (Change the volume path to your local directory structure)
2. Copy .env.example to .env and fill out the Settings.
3. Build and run the docker via docker-compose


## Notice

Please be aware that this tool was designed to interact with Openhab. If you do not use Openhab you have to comment out 'openhab' in the settings.py, section INSTALLED_APPS.


