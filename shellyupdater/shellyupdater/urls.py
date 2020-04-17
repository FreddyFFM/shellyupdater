"""shellyupdater URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import home.urls
import updates.urls
import setter.urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
]

urlpatterns += [
    path('', include(home.urls)),
    path('shellies/', include(updates.urls)),
    path('settings/', include(setter.urls)),
]

if 'openhab' in settings.INSTALLED_APPS:

    import openhab.urls
    urlpatterns += [
        path('things/', include(openhab.urls)),
    ]

urlpatterns += staticfiles_urlpatterns()

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns = [
#         path('__debug__/', include(debug_toolbar.urls)),
#
#     ] + urlpatterns