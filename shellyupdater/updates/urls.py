from .views import ShowShelliesView, OpenhabThingsView, ShellyDetailView
from django.urls import path, re_path

urlpatterns = [
    path('', ShowShelliesView.as_view(), name="home"),
    re_path('^(?P<refresh>[Y]+)/$', ShowShelliesView.as_view(), name="home"),

    path('things', OpenhabThingsView.as_view(), name="things"),
    re_path('^things/(?P<refresh>[Y]+)/$', OpenhabThingsView.as_view(), name="things"),

    re_path('^details/(?P<shelly_id>[\w\-]+)/$', ShellyDetailView.as_view(), name="details"),
    re_path('^details/(?P<shelly_id>[\w\-]+)/(?P<refresh>[Y]+)/$', ShellyDetailView.as_view(), name="details"),
]
