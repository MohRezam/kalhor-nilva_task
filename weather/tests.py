from django.test import TestCase, Client
from rest_framework import status

class WeatherViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_weather(self):
        lat = 37.7749  
        lon = -122.4194  

        response = self.client.get(f'/api/weather/full?lat={lat}&lon={lon}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('location_name', response.data)
        self.assertIn('date', response.data)
        self.assertIn('temp', response.data)
        self.assertIn('weather', response.data)
