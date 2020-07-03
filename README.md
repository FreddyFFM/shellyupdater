# ShellyUpdater

## What is ShellyUpdater?

As I do setup my Shelly manually via the http-interface and add them to my MQTT broker (I do not use the Shelly Cloud 
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
* Possibility to mass-update Shelly-Settings via http (postponed for retry when Shelly is offline)
    * Includes General settings (like mqtt)
    * Wifi AP, Wifi Client and Wifi Backup
    * as well as login data
    * and some spefic settings for Door/Window
* Integrates with MQTT and subscribes to the announcements, online and battery status
* Option to integrate with Openhab (Overview on Shelly-Things) via the Openhab REST API


## How to use/install?

I did not setup everything to run immediately after cloning the repo, but with some small steps you can run it in a docker container via docker-compose.

1. Change docker-compose.yaml\
   (Change the volume path to your local directory structure)\
   ```
   volumes:
   - /etc/localtime:/etc/localtime:ro
   - ./data:/home/updater/data 
   # Change ./data to your local path
   
2. Copy .env.example to .env and fill out the Settings.\
    ```
   cp .env.example .env
   # Change the variables in .env to your needs
   
3. Build and run the docker via docker-compose
    ```
   docker-compose build shellyupdate
   docker-compose up shellyupdater &

## Notice

Please be aware that this tool was designed to interact with Openhab. If you do not use Openhab you have to comment out 'openhab' in the settings.py, section INSTALLED_APPS.


