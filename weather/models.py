from django.db import models
from decimal import Decimal

class WeatherData(models.Model):
    city = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=20, decimal_places=14)
    longitude = models.DecimalField(max_digits=20, decimal_places=14)
    data = models.JSONField()
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['latitude', 'longitude']
    
        
    def __str__(self):
        return f"{self.city}-{self.timestamp}-{self.latitude}-{self.longitude}"