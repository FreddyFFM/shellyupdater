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
