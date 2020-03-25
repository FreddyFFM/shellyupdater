#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-

from django.conf import settings


def openhab_active(request):

    if 'openhab' in settings.INSTALLED_APPS:
        oh_active = True
    else:
        oh_active = False

    return {
        'OH_ACTIVE' : oh_active
    }
