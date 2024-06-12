from django.urls import path
from . import views

urlpatterns = [
    path('weather/full', views.WeatherView.as_view(), name='weather_data'),
]
