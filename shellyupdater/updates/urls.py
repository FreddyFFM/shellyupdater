from .views import ShowShelliesView, ShellyDetailView
from django.urls import path, re_path

urlpatterns = [
    path('', ShowShelliesView.as_view(), name="shellies"),
    re_path('^(?P<refresh>[Y]+)/$', ShowShelliesView.as_view(), name="shellies"),

    re_path('^details/$', ShellyDetailView.as_view(), name="shellies/details"),
    re_path('^details/(?P<shelly_id>[\w\-]+)/$', ShellyDetailView.as_view(), name="shellies/details"),
    re_path('^details/(?P<shelly_id>[\w\-]+)/(?P<refresh>[Y]+)/$', ShellyDetailView.as_view(), name="shellies/details"),
]
