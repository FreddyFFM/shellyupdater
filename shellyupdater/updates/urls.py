from .views import ShowShelliesView, OpenhabThingsView, ShellyDetailView, HomeView
from django.urls import path, re_path

urlpatterns = [
    path('', HomeView.as_view(), name="home"),

    path('shellies', ShowShelliesView.as_view(), name="shellies"),
    re_path('^shellies/(?P<refresh>[Y]+)/$', ShowShelliesView.as_view(), name="shellies"),

    re_path('^shellies/details/(?P<shelly_id>[\w\-]+)/$', ShellyDetailView.as_view(), name="shellies/details"),
    re_path('^shellies/details/(?P<shelly_id>[\w\-]+)/(?P<refresh>[Y]+)/$', ShellyDetailView.as_view(), name="shellies/details"),

    path('things', OpenhabThingsView.as_view(), name="things"),
    re_path('^things/(?P<refresh>[Y]+)/$', OpenhabThingsView.as_view(), name="things"),

]
