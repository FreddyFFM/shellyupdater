from .views import ShowShelliesView, OpenhabThingsView
from django.urls import path, re_path

urlpatterns = [
    path('', ShowShelliesView.as_view(), name="home"),
    re_path('^(?P<refresh>[Y]+)/$', ShowShelliesView.as_view(), name="home"),

    path('things', OpenhabThingsView.as_view(), name="things"),
    re_path('^things/(?P<refresh>[Y]+)/$', OpenhabThingsView.as_view(), name="things"),
]
