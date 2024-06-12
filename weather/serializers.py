from rest_framework import serializers

class CurrentWeatherSerializer(serializers.Serializer):
    date = serializers.IntegerField(source='dt')
    location_name = serializers.CharField(source='name')
    temp = serializers.SerializerMethodField()
    weather = serializers.SerializerMethodField()
    wind = serializers.DictField(child=serializers.FloatField())
    humidity = serializers.SerializerMethodField()
    pressure = serializers.SerializerMethodField()
    sunrise = serializers.SerializerMethodField()
    sunset = serializers.SerializerMethodField()

    def get_temp(self, data):
        return {
            "now": f"{data['main']['temp'] - 273.15:.2f}",
            "min": f"{data['main']['temp_min'] - 273.15:.2f}",
            "max": f"{data['main']['temp_max'] - 273.15:.2f}"
        }

    def get_weather(self, data):
        return {"icon_type": data['weather'][0]['description']}
    
    def get_humidity(self, data):
        return data["main"]["humidity"]
    def get_pressure(self, data):
        return data["main"]["pressure"]
    def get_sunrise(self, data):
        return data["sys"]["sunrise"]
    def get_sunset(self, data):
        return data["sys"]["sunset"]


class HourlyForecastSerializer(serializers.Serializer):
    future_hours = serializers.SerializerMethodField()

    def get_future_hours(self, data):
        formated_data = {}
        for i in range(5):
            formated_data[str(i)] = {
                'date': data['list'][i]["dt"],
                 "temp": round(data['list'][i]["main"]["temp"] - 273.15),
                'weather': {
                    "icon_type": data['list'][i]['weather'][0]['description']
                }
            }
        return formated_data



class DailyForecastSerializer(serializers.Serializer):
    future_days = serializers.SerializerMethodField()

    def get_future_days(self, data):
        formated_data = {}
        for i in range(5):  
            formated_data[str(i)] = {
                'date': data['list'][i]["dt"],
                'temp': {
                      "min": f'{data["list"][i]["temp"]["min"] - 273.15:.2f}',
                      "max": f'{data["list"][i]["temp"]["max"] - 273.15:.2f}'
                },
                'weather': {
                    "icon_type": data["list"][i]['weather'][0]['description']
                }
            }
        return formated_data




# from rest_framework import serializers
# from .models import WeatherData

# class WeatherDataSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = WeatherData
#         fields = ["data", "timestamp"]



