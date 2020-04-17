# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class Shellies (models.Model):
    """
    Base model for the Shellies
    """

    def __str__(self):
        val = self.shelly_id
        things = OpenHabThings.objects.filter(shelly_id=self.id)
        if things:
            val = val + " (" + things[0].thing_label + ")"
        return val

    def get_fw_short(self):
        return self.shelly_fw_version.split('/')[1]

    id = models.AutoField(primary_key=True)
    shelly_id = models.CharField(max_length=100, blank=False, null=False, unique=True)
    shelly_name = models.CharField(max_length=200, blank=True, null=True)
    shelly_mac = models.CharField(max_length=50, blank=True, null=True)
    shelly_ip = models.CharField(max_length=50, blank=True, null=True)
    shelly_new_fw = models.BooleanField(default=False)
    shelly_fw_version = models.CharField(max_length=100, blank=True, null=True)
    shelly_fw_version_old = models.CharField(max_length=100, blank=True, null=True)
    shelly_fw_version_new = models.CharField(max_length=100, blank=True, null=True)
    shelly_type = models.CharField(max_length=100, blank=True, null=True)
    shelly_online = models.BooleanField(default=False)
    shelly_last_online = models.DateTimeField(1)
    shelly_do_update = models.BooleanField(default=False)
    last_change_ts = models.DateTimeField(auto_now=True)
    last_status = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'shellies'


class ShellySettings (models.Model):
    """
    Base model for the Shellies
    """

    id = models.AutoField(primary_key=True)
    shelly_id = models.OneToOneField(Shellies, on_delete=models.CASCADE, related_name="shelly2infos")
    shelly_settings_json = models.TextField(null=True, blank=True)
    shelly_status_json = models.TextField(null=True, blank=True)
    shelly_battery_percent = models.IntegerField(null=True, blank=True)
    shelly_battery_voltage = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    last_change_ts = models.DateTimeField(auto_now=True)
    last_status_settings = models.CharField(max_length=200, blank=True, null=True)
    last_status_status = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'shellies_settings'


class ShellySettingUpdates(models.Model):
    """

    """

    id = models.AutoField(primary_key=True)
    shelly_id = models.ForeignKey(Shellies, on_delete=models.CASCADE, related_name="shelly2updates")
    shelly_settings_path = models.CharField(max_length=200, blank=False, null=False)
    shelly_settings_json = models.TextField(null=False, blank=False)
    shelly_settings_encoded = models.TextField(null=False, blank=False)
    shelly_settings_applied = models.BooleanField(default=False)
    shelly_settings_delete = models.BooleanField(default=False)
    insert_ts = models.DateTimeField(auto_now_add=True)
    last_status_ts = models.DateTimeField(auto_now=True)
    last_status = models.CharField(max_length=200, blank=True, null=True)
    last_status_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'shellies_settings_updates'


class OpenHabThings (models.Model):
    """

    """

    id = models.AutoField(primary_key=True)
    thing_uid = models.CharField(max_length=100, blank=False, null=False, unique=True)
    thing_label = models.CharField(max_length=200, blank=False, null=False)
    thing_location = models.CharField(max_length=100, blank=True, null=True)
    shelly_id = models.ForeignKey(Shellies, on_delete=models.DO_NOTHING, null=True, related_name="shelly2thing")
    last_change_ts = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'openhab_things'


class MasterDataShellySettings(models.Model):

    SETTINGS_TYPE_CHOICES = (
        ('General', 'General settings'),
        ('WifiAP', 'Internal Wifi AP'),
        ('Wifi1', 'Wifi Connection'),
        ('Wifi2', 'Wifi Connection Backup'),
        ('Login', 'Credentials')
    )

    SETTINGS_PARAM_TYPE_CHOICES = (
        ('bool', 'Boolean'),
        ('string', 'String'),
        ('number', 'Number'),
    )

    id = models.AutoField(primary_key=True)
    md_settings_type = models.CharField(max_length=50, null=False, blank=False, choices=SETTINGS_TYPE_CHOICES)
    md_settings_path = models.CharField(max_length=100, blank=False, null=False)
    md_settings_parameter = models.CharField(max_length=100, blank=False, null=False)
    md_settings_parameter_type = models.CharField(max_length=100, blank=False, null=False, choices=SETTINGS_PARAM_TYPE_CHOICES)
    md_settings_description = models.CharField(max_length=250, blank=True, null=True)
    md_settings_single = models.BooleanField(default=False)
    md_settings_reference_path = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        unique_together = ('md_settings_path', 'md_settings_parameter',)
        db_table = 'masterdata_shelly_settings'


class MasterDataShellySettingsMatrix(models.Model):

    SHELLY_DEVICES = (
        ('SHELLY1','Shelly1'),
        ('SHELLY1PM', 'Shelly1 PM'),
        ('SHELLYSWITCH', 'Shelly2'),
        ('SHELLYSWITCH25', 'Shelly2.5'),
        ('SHELLY4PRO', 'Shelly 4Pro'),
        ('SHELLYPLUG', 'Shelly Plug'),
        ('SHELLYPLUG-S', 'Shelly Plug S'),
        ('SHELLYVINTAGE', 'Shelly Vintage'),
        ('SHELLYRGBW2', 'Shelly RGBW2'),
        ('SHELLYDIMMER', 'Shelly Dimmer'),
        ('SHELLYSENSE', 'Shelly Sense'),
        ('SHELLYHT', 'Shelly H&T'),
        ('SHELLYSMOKE', 'Shelly Smoke'),
        ('SHELLYEM', 'Shelly EM'),
        ('SHELLYEM3', 'Shelly 3EM'),
        ('SHELLYFLOOD', 'Shelly Flood'),
        ('SHELLYDW', 'Shelly Door/Window'),
    )

    md_setmatrix_setting = models.ForeignKey(MasterDataShellySettings, on_delete=models.CASCADE, null=False, related_name="settingsmatrix")
    md_setmatrix_shellytype = models.CharField(max_length=30, blank=False, null=False, choices=SHELLY_DEVICES)

    class Meta:
        managed = True
        unique_together = ('md_setmatrix_setting', 'md_setmatrix_shellytype',)
        db_table = 'masterdata_shelly_settings_matrix'

