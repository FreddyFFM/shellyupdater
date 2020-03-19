from .views import ShowShelliesView
from django.urls import path, re_path

urlpatterns = [
    path('', ShowShelliesView.as_view(), name="home"),
re_path('^(?P<refresh>[Y]+)/$', ShowShelliesView.as_view(), name="home"),
]