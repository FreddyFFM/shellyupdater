from .views import HomeView
from django.urls import path, re_path

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
]
