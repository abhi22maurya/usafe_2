import requests
import json
from datetime import datetime, timedelta
from config import WEATHER_CONFIG
import logging
from typing import Dict, List, Optional

class WeatherHistoryService:
    def __init__(self):
        self.api_key = WEATHER_CONFIG['api_key']
        self.base_url = WEATHER_CONFIG['base_url']
        self.units = WEATHER_CONFIG['units']
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='logs/weather_history_service.log'
        )
        self.logger = logging.getLogger(__name__)

    def get_weather_history(self, lat: float, lon: float, start_date: datetime, end_date: datetime) -> Dict:
        """Get weather history for a specific location and time range"""
        try:
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                raise ValueError("Invalid coordinates")

            if end_date <= start_date:
                raise ValueError("End date must be after start date")

            # OpenWeatherMap API has a limit of 5 days per request
            max_days = 5
            total_days = (end_date - start_date).days
            num_requests = (total_days // max_days) + 1

            all_data = []
            current_start = start_date

            for _ in range(num_requests):
                current_end = current_start + timedelta(days=max_days)
                if current_end > end_date:
                    current_end = end_date

                data = self._get_weather_data(lat, lon, current_start, current_end)
                all_data.extend(data)
                
                if current_end >= end_date:
                    break
                current_start = current_end

            return self._process_history_data(all_data)

        except requests.RequestException as e:
            self.logger.error(f"Weather history request failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error getting weather history: {str(e)}")
            raise

    def _get_weather_data(self, lat: float, lon: float, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get weather data for a specific time range"""
        url = f"{self.base_url}/data/2.5/onecall/timemachine"
        
        # Convert dates to timestamps
        start_ts = int(start_date.timestamp())
        end_ts = int(end_date.timestamp())
        
        # Get data for each day in the range
        data = []
        current_ts = start_ts
        
        while current_ts < end_ts:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'dt': current_ts,
                'units': self.units
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if 'current' in result:
                data.append(result['current'])
            
            # Move to next day
            current_ts += 86400  # 24 hours in seconds
            
        return data

    def _process_history_data(self, data: List[Dict]) -> Dict:
        """Process and format the historical weather data"""
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

        for day in data:
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

    def get_monthly_summary(self, lat: float, lon: float, year: int, month: int) -> Dict:
        """Get monthly weather summary for a specific location"""
        try:
            # Calculate date range for the month
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)

            data = self.get_weather_history(lat, lon, start_date, end_date)
            return self._process_monthly_summary(data)

        except Exception as e:
            self.logger.error(f"Error getting monthly summary: {str(e)}")
            raise

    def _process_monthly_summary(self, data: Dict) -> Dict:
        """Process and format the monthly summary"""
        summary = {
            'temperature': {
                'min': data['summary']['temperature']['min'],
                'max': data['summary']['temperature']['max'],
                'avg': data['summary']['temperature']['avg']
            },
            'humidity': {
                'min': data['summary']['humidity']['min'],
                'max': data['summary']['humidity']['max'],
                'avg': data['summary']['humidity']['avg']
            },
            'precipitation': {
                'total': data['summary']['precipitation']['total'],
                'days_with_rain': data['summary']['precipitation']['days_with_rain']
            },
            'temperature_trend': self._calculate_temperature_trend(data['daily']),
            'humidity_trend': self._calculate_humidity_trend(data['daily'])
        }

        return summary

    def _calculate_temperature_trend(self, daily_data: List[Dict]) -> Dict:
        """Calculate temperature trend over the month"""
        if not daily_data:
            return {'slope': 0.0, 'trend': 'stable'}

        # Calculate daily temperature changes
        temp_changes = []
        for i in range(1, len(daily_data)):
            change = daily_data[i]['temperature']['avg'] - daily_data[i-1]['temperature']['avg']
            temp_changes.append(change)

        # Calculate average change
        avg_change = sum(temp_changes) / len(temp_changes)

        # Determine trend
        if avg_change > 0.5:  # More than 0.5°C per day
            trend = 'increasing'
        elif avg_change < -0.5:  # Less than -0.5°C per day
            trend = 'decreasing'
        else:
            trend = 'stable'

        return {'slope': avg_change, 'trend': trend}

    def _calculate_humidity_trend(self, daily_data: List[Dict]) -> Dict:
        """Calculate humidity trend over the month"""
        if not daily_data:
            return {'slope': 0.0, 'trend': 'stable'}

        # Calculate daily humidity changes
        humidity_changes = []
        for i in range(1, len(daily_data)):
            change = daily_data[i]['humidity'] - daily_data[i-1]['humidity']
            humidity_changes.append(change)

        # Calculate average change
        avg_change = sum(humidity_changes) / len(humidity_changes)

        # Determine trend
        if avg_change > 5:  # More than 5% per day
            trend = 'increasing'
        elif avg_change < -5:  # Less than -5% per day
            trend = 'decreasing'
        else:
            trend = 'stable'

        return {'slope': avg_change, 'trend': trend}
