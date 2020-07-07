#!/bin/sh
echo "Start DB Migration"
python manage.py migrate
echo "Load Masterdata"
python manage.py loaddata MasterDataShellySettings.json
echo "Load Masterdata Matrix"
python manage.py loaddata MasterDataShellySettingsMatrix.json
echo "Finished"
