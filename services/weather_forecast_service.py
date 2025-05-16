import requests
import json
from datetime import datetime, timedelta
from config import WEATHER_CONFIG
import logging
from typing import Dict, List, Optional

class WeatherForecastService:
    def __init__(self):
        self.api_key = WEATHER_CONFIG['api_key']
        self.base_url = WEATHER_CONFIG['base_url']
        self.units = WEATHER_CONFIG['units']
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='logs/weather_forecast_service.log'
        )
        self.logger = logging.getLogger(__name__)

    def get_weather_forecast(self, lat: float, lon: float, days: int = 7) -> Dict:
        """Get weather forecast for a specific location"""
        try:
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                raise ValueError("Invalid coordinates")

            if days < 1 or days > 14:
                raise ValueError("Days must be between 1 and 14")

            url = f"{self.base_url}/onecall"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'exclude': 'current,minutely,hourly,alerts',
                'units': self.units
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'daily' in data:
                return self._process_forecast_data(data['daily'][:days])
            else:
                raise ValueError("No forecast data available")

        except requests.RequestException as e:
            self.logger.error(f"Weather forecast request failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error getting weather forecast: {str(e)}")
            raise

    def _process_forecast_data(self, daily_data: List[Dict]) -> Dict:
        """Process and format the forecast data"""
        processed_data = {
            'daily': [],
            'summary': {
                'temperature': {
                    'min': float('inf'),
                    'max': float('-inf'),
                    'avg': 0.0
                },
                'humidity': {
                    'min': float('inf'),
                    'max': float('-inf'),
                    'avg': 0.0
                },
                'precipitation': {
                    'total': 0.0,
                    'days_with_rain': 0
                }
            }
        }

        for day in daily_data:
            processed_day = {
                'date': datetime.fromtimestamp(day['dt']).isoformat(),
                'temperature': {
                    'min': day['temp']['min'],
                    'max': day['temp']['max'],
                    'avg': (day['temp']['min'] + day['temp']['max']) / 2
                },
                'humidity': day['humidity'],
                'description': day['weather'][0]['description'],
                'icon': day['weather'][0]['icon'],
                'precipitation': {
                    'probability': day.get('pop', 0.0) * 100,
                    'amount': day.get('rain', {}).get('1h', 0.0)
                }
            }

            # Update summary statistics
            processed_data['summary']['temperature']['min'] = min(
                processed_data['summary']['temperature']['min'],
                processed_day['temperature']['min']
            )
            processed_data['summary']['temperature']['max'] = max(
                processed_data['summary']['temperature']['max'],
                processed_day['temperature']['max']
            )
            processed_data['summary']['temperature']['avg'] += processed_day['temperature']['avg']

            processed_data['summary']['humidity']['min'] = min(
                processed_data['summary']['humidity']['min'],
                processed_day['humidity']
            )
            processed_data['summary']['humidity']['max'] = max(
                processed_data['summary']['humidity']['max'],
                processed_day['humidity']
            )
            processed_data['summary']['humidity']['avg'] += processed_day['humidity']

            if processed_day['precipitation']['amount'] > 0:
                processed_data['summary']['precipitation']['days_with_rain'] += 1
            processed_data['summary']['precipitation']['total'] += processed_day['precipitation']['amount']

            processed_data['daily'].append(processed_day)

        # Calculate averages
        num_days = len(processed_data['daily'])
        if num_days > 0:
            processed_data['summary']['temperature']['avg'] /= num_days
            processed_data['summary']['humidity']['avg'] /= num_days

        return processed_data

    def get_hourly_forecast(self, lat: float, lon: float) -> Dict:
        """Get hourly weather forecast for a specific location"""
        try:
            url = f"{self.base_url}/onecall"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'exclude': 'current,daily,alerts',
                'units': self.units
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'hourly' in data:
                return self._process_hourly_data(data['hourly'][:24])  # Get next 24 hours
            else:
                raise ValueError("No hourly forecast data available")

        except requests.RequestException as e:
            self.logger.error(f"Hourly forecast request failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error getting hourly forecast: {str(e)}")
            raise

    def _process_hourly_data(self, hourly_data: List[Dict]) -> Dict:
        """Process and format the hourly forecast data"""
        processed_data = {
            'hourly': [],
            'summary': {
                'temperature': {
                    'min': float('inf'),
                    'max': float('-inf'),
                    'avg': 0.0
                },
                'humidity': {
                    'min': float('inf'),
                    'max': float('-inf'),
                    'avg': 0.0
                },
                'precipitation': {
                    'total': 0.0,
                    'hours_with_rain': 0
                }
            }
        }

        for hour in hourly_data:
            processed_hour = {
                'time': datetime.fromtimestamp(hour['dt']).isoformat(),
                'temperature': hour['temp'],
                'humidity': hour['humidity'],
                'description': hour['weather'][0]['description'],
                'icon': hour['weather'][0]['icon'],
                'precipitation': {
                    'probability': hour.get('pop', 0.0) * 100,
                    'amount': hour.get('rain', {}).get('1h', 0.0)
                }
            }

            # Update summary statistics
            processed_data['summary']['temperature']['min'] = min(
                processed_data['summary']['temperature']['min'],
                processed_hour['temperature']
            )
            processed_data['summary']['temperature']['max'] = max(
                processed_data['summary']['temperature']['max'],
                processed_hour['temperature']
            )
            processed_data['summary']['temperature']['avg'] += processed_hour['temperature']

            processed_data['summary']['humidity']['min'] = min(
                processed_data['summary']['humidity']['min'],
                processed_hour['humidity']
            )
            processed_data['summary']['humidity']['max'] = max(
                processed_data['summary']['humidity']['max'],
                processed_hour['humidity']
            )
            processed_data['summary']['humidity']['avg'] += processed_hour['humidity']

            if processed_hour['precipitation']['amount'] > 0:
                processed_data['summary']['precipitation']['hours_with_rain'] += 1
            processed_data['summary']['precipitation']['total'] += processed_hour['precipitation']['amount']

            processed_data['hourly'].append(processed_hour)

        # Calculate averages
        num_hours = len(processed_data['hourly'])
        if num_hours > 0:
            processed_data['summary']['temperature']['avg'] /= num_hours
            processed_data['summary']['humidity']['avg'] /= num_hours

        return processed_data
