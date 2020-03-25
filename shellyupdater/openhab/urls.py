from .views import OpenhabThingsView
from django.urls import path, re_path

urlpatterns = [
    path('', OpenhabThingsView.as_view(), name="things"),
    re_path('^(?P<refresh>[Y]+)/$', OpenhabThingsView.as_view(), name="things"),
]
