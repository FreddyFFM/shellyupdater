# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class Shellies (models.Model):
    """
    Base model for the Shellies
    """

    id = models.AutoField(primary_key=True)
    shelly_id = models.CharField(max_length=100, blank=False, null=False, unique=True)
    shelly_name = models.CharField(max_length=200, blank=True, null=True)
    shelly_mac = models.CharField(max_length=50, blank=True, null=True)
    shelly_ip = models.CharField(max_length=50, blank=True, null=True)
    shelly_new_fw = models.BooleanField(default=False)
    shelly_fw_version = models.CharField(max_length=100, blank=True, null=True)
    shelly_type = models.CharField(max_length=100, blank=True, null=True)
    shelly_online = models.BooleanField(default=False)
    shelly_last_online = models.DateTimeField(1)
    shelly_do_update = models.BooleanField(default=False)
    last_change_ts = models.DateTimeField(auto_now=True)
    last_status = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'shellies'


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


class ShellySettings (models.Model):
    """
    Base model for the Shellies
    """

    id = models.AutoField(primary_key=True)
    shelly_id = models.OneToOneField(Shellies, on_delete=models.CASCADE, related_name="shelly2infos")
    shelly_settings_json = models.TextField(null=True, blank=True)
    shelly_status_json = models.TextField(null=True, blank=True)
    last_change_ts = models.DateTimeField(auto_now=True)
    last_status_settings = models.CharField(max_length=200, blank=True, null=True)
    last_status_status = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'shellies_settings'
