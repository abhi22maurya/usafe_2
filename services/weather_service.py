import os
import requests
from datetime import datetime, timedelta
import logging

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.cache = {}
        self.cache_duration = timedelta(minutes=10)
        
    def get_current_weather(self, lat, lon):
        try:
            # Check cache first
            cache_key = f"weather_{lat}_{lon}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if datetime.now() - timestamp < self.cache_duration:
                    return cached_data
            
            # Make API call
            url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process and cache the response
            weather_data = {
                'temperature': data['main']['temp'],
                'conditions': data['weather'][0]['description'],
                'wind_speed': data['wind']['speed'],
                'humidity': data['main']['humidity']
            }
            
            self.cache[cache_key] = (weather_data, datetime.now())
            return weather_data
            
        except Exception as e:
            logging.error(f"Error getting weather data: {str(e)}")
            return {
                'temperature': 'N/A',
                'conditions': 'N/A',
                'wind_speed': 'N/A',
                'humidity': 'N/A'
            } 