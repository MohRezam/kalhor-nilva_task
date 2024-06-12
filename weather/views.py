import aiohttp
import asyncio
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .serializers import CurrentWeatherSerializer, HourlyForecastSerializer, DailyForecastSerializer
from rest_framework import status

API_KEY = '491b06a17c29904489eaa96476cd3dcd'
CURRENT_WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'
HOURLY_FORECAST_URL = 'https://pro.openweathermap.org/data/2.5/forecast/hourly'
DAILY_FORECAST_URL = 'https://api.openweathermap.org/data/2.5/forecast/daily'

async def fetch_json(session, url, params):
    async with session.get(url, params=params) as response:
        if response.status != 200:
            raise aiohttp.ClientResponseError(status=response.status, message=response.reason)
        return await response.json()

async def get_current_weather_async(lat, lon):
    async with aiohttp.ClientSession() as session:
        params = {'lat': lat, 'lon': lon, 'appid': API_KEY}
        return await fetch_json(session, CURRENT_WEATHER_URL, params)

async def get_hourly_forecast_async(lat, lon):
    async with aiohttp.ClientSession() as session:
        params = {'lat': lat, 'lon': lon, 'appid': API_KEY}
        return await fetch_json(session, HOURLY_FORECAST_URL, params)

async def get_daily_forecast_async(lat, lon):
    async with aiohttp.ClientSession() as session:
        params = {'lat': lat, 'lon': lon, 'appid': API_KEY}
        return await fetch_json(session, DAILY_FORECAST_URL, params)

def get_cached_weather_data(lat, lon, future_days_only=False):
    cache_keys = cache.keys('weather_data_*')
    for key in cache_keys:
        cached_lat_lon = key.split('_')[-2:]
        cached_lat, cached_lon = map(float, cached_lat_lon)
        if cached_lat == lat and cached_lon == lon:
            if future_days_only and "future_days" not in key:
                continue
            elif future_days_only == False and "future_days" in key:
                continue
            return cache.get(key)
    return None

class WeatherView(APIView):
    def get(self, request, format=None):
        lat = request.GET.get('lat')
        lon = request.GET.get('lon')
        lat = round(float(lat), 5)
        lon = round(float(lon), 5)
        
        if not lat or not lon:
            return Response({'error': 'Latitude and longitude are required'}, status=status.HTTP_400_BAD_REQUEST)

        cached_current_hours = get_cached_weather_data(lat, lon, future_days_only=False)
        cached_future_days_data = get_cached_weather_data(lat, lon, future_days_only=True)

        if cached_current_hours and cached_future_days_data:
            return Response({
                **cached_current_hours,
                **cached_future_days_data
            }, status=status.HTTP_200_OK)

        try:
            current_data = None
            future_hours = None
            future_days = None

            if not cached_current_hours:
                current_weather_data = asyncio.run(get_current_weather_async(lat, lon))
                current_data = CurrentWeatherSerializer(current_weather_data).data

                hourly_forecast_data = asyncio.run(get_hourly_forecast_async(lat, lon))
                future_hours = HourlyForecastSerializer(hourly_forecast_data).data
            
            if not cached_future_days_data:
                daily_forecast_data = asyncio.run(get_daily_forecast_async(lat, lon))
                future_days = DailyForecastSerializer(daily_forecast_data).data

            formatted_data = {
                **current_data,
                **future_hours,
                **(future_days or cached_future_days_data)
            }

            cache.set(f"weather_data_{lat}_{lon}", formatted_data, timeout=60 * 60)   
            cache.set(f"weather_data_future_days_{lat}_{lon}", future_days, timeout=60 * 60 * 24)  

            return Response(formatted_data, status=status.HTTP_200_OK)

        except aiohttp.ClientResponseError as e:
            return Response({'error': f'Failed to fetch data from OpenWeatherMap API: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': f'An error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# from django.core.cache import cache
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework import status
# from .serializers import CurrentWeatherSerializer, HourlyForecastSerializer, DailyForecastSerializer
# from celery import shared_task
# import aiohttp


# API_KEY = '491b06a17c29904489eaa96476cd3dcd'
# CURRENT_WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'
# HOURLY_FORECAST_URL = 'https://pro.openweathermap.org/data/2.5/forecast/hourly'
# DAILY_FORECAST_URL = 'https://api.openweathermap.org/data/2.5/forecast/daily'


# async def fetch_json(session, url, params):
#     async with session.get(url, params=params) as response:
#         if response.status != 200:
#             raise aiohttp.ClientResponseError(status=response.status, message=response.reason)
#         return await response.json()

# def sync_fetch_json(url, params):
#     async def fetch():
#         async with aiohttp.ClientSession() as session:
#             return await fetch_json(session, url, params)
#     return asyncio.run(fetch())

# @shared_task
# def fetch_current_weather(lat, lon):
#     params = {'lat': lat, 'lon': lon, 'appid': API_KEY}
#     return sync_fetch_json(CURRENT_WEATHER_URL, params)

# @shared_task
# def fetch_hourly_forecast(lat, lon):
#     params = {'lat': lat, 'lon': lon, 'appid': API_KEY}
#     return sync_fetch_json(HOURLY_FORECAST_URL, params)

# @shared_task
# def fetch_daily_forecast(lat, lon):
#     params = {'lat': lat, 'lon': lon, 'appid': API_KEY}
#     return sync_fetch_json(DAILY_FORECAST_URL, params)


# import asyncio
# from django.core.cache import cache
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework import status
# from .serializers import CurrentWeatherSerializer, HourlyForecastSerializer, DailyForecastSerializer

# API_KEY = '491b06a17c29904489eaa96476cd3dcd'
# CURRENT_WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'
# HOURLY_FORECAST_URL = 'https://pro.openweathermap.org/data/2.5/forecast/hourly'
# DAILY_FORECAST_URL = 'https://api.openweathermap.org/data/2.5/forecast/daily'

# def get_cached_weather_data(lat, lon, future_days_only=False):
#     cache_keys = cache.keys('weather_data_*')
#     for key in cache_keys:
#         cached_lat_lon = key.split('_')[-2:]
#         cached_lat, cached_lon = map(float, cached_lat_lon)
#         if cached_lat == lat and cached_lon == lon:
#             if future_days_only and "future_days" not in key:
#                 continue
#             elif future_days_only == False and "future_days" in key:
#                 continue
#             return cache.get(key)
#     return None

# class WeatherView(APIView):
#     def get(self, request, format=None):
#         lat = request.GET.get('lat')
#         lon = request.GET.get('lon')
#         lat = round(float(lat), 5)
#         lon = round(float(lon), 5)

#         if not lat or not lon:
#             return Response({'error': 'Latitude and longitude are required'}, status=status.HTTP_400_BAD_REQUEST)

#         cached_current_hours = get_cached_weather_data(lat, lon, future_days_only=False)
#         cached_future_days_data = get_cached_weather_data(lat, lon, future_days_only=True)

#         if cached_current_hours and cached_future_days_data:
#             return Response({
#                 **cached_current_hours,
#                 **cached_future_days_data
#             }, status=status.HTTP_200_OK)

#         try:
#             current_data = None
#             future_hours = None
#             future_days = None

#             if not cached_current_hours:
#                 current_weather_data = fetch_current_weather.delay(lat, lon).get()
#                 current_data = CurrentWeatherSerializer(current_weather_data).data

#                 hourly_forecast_data = fetch_hourly_forecast.delay(lat, lon).get()
#                 future_hours = HourlyForecastSerializer(hourly_forecast_data).data

#             if not cached_future_days_data:
#                 daily_forecast_data = fetch_daily_forecast.delay(lat, lon).get()
#                 future_days = DailyForecastSerializer(daily_forecast_data).data

#             formatted_data = {
#                 **current_data,
#                 **future_hours,
#                 **(future_days or cached_future_days_data)
#             }

#             cache.set(f"weather_data_{lat}_{lon}", formatted_data, timeout=60 * 60)
#             cache.set(f"weather_data_future_days_{lat}_{lon}", future_days, timeout=60 * 60 * 24)

#             return Response(formatted_data, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({'error': f'An error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




        





