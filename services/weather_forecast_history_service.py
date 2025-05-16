import requests
import json
from datetime import datetime, timedelta
from config import WEATHER_CONFIG
import logging
from typing import Dict, List, Optional

class WeatherForecastHistoryService:
    def __init__(self):
        self.api_key = WEATHER_CONFIG['api_key']
        self.base_url = WEATHER_CONFIG['base_url']
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='logs/weather_forecast_history_service.log'
        )
        self.logger = logging.getLogger(__name__)

    def get_forecast_history(self, lat: float, lon: float, days: int = 7) -> Dict:
        """Get historical weather forecasts for a location"""
        try:
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                raise ValueError("Invalid coordinates")

            if days < 1 or days > 30:
                raise ValueError("Days must be between 1 and 30")

            # Get current forecast as reference
            current_forecast = self._get_current_forecast(lat, lon)
            
            # Get historical forecasts
            historical_forecasts = []
            for i in range(days):
                date = datetime.now() - timedelta(days=i)
                forecast = self._get_historical_forecast(lat, lon, date)
                historical_forecasts.append(forecast)

            return {
                'current_forecast': current_forecast,
                'historical_forecasts': historical_forecasts,
                'accuracy_metrics': self._calculate_accuracy_metrics(
                    current_forecast,
                    historical_forecasts
                )
            }

        except requests.RequestException as e:
            self.logger.error(f"Forecast history request failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error getting forecast history: {str(e)}")
            raise

    def _get_current_forecast(self, lat: float, lon: float) -> Dict:
        """Get current weather forecast"""
        url = f"{self.base_url}/onecall"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'exclude': 'current,minutely,hourly,alerts',
            'units': 'metric'
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        return self._process_forecast_data(data['daily'][:7])  # Get next 7 days

    def _get_historical_forecast(self, lat: float, lon: float, date: datetime) -> Dict:
        """Get historical weather forecast for a specific date"""
        url = f"{self.base_url}/data/2.5/onecall/timemachine"
        
        # Convert date to timestamp
        timestamp = int(date.timestamp())
        
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'dt': timestamp,
            'units': 'metric'
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        return self._process_forecast_data(data['daily'][:7])  # Get next 7 days

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

    def _calculate_accuracy_metrics(self, current_forecast: Dict, historical_forecasts: List[Dict]) -> Dict:
        """Calculate accuracy metrics for weather forecasts"""
        metrics = {
            'temperature': {
                'mae': 0.0,
                'mse': 0.0,
                'rmse': 0.0
            },
            'humidity': {
                'mae': 0.0,
                'mse': 0.0,
                'rmse': 0.0
            },
            'precipitation': {
                'accuracy': 0.0,
                'false_positives': 0,
                'false_negatives': 0
            }
        }

        # Calculate metrics for each day
        for i in range(len(current_forecast['daily'])):
            current_day = current_forecast['daily'][i]
            
            # Calculate temperature metrics
            temp_errors = []
            for hist in historical_forecasts:
                if i < len(hist['daily']):
                    hist_day = hist['daily'][i]
                    error = abs(current_day['temperature']['avg'] - hist_day['temperature']['avg'])
                    temp_errors.append(error)
            
            if temp_errors:
                mae = sum(temp_errors) / len(temp_errors)
                mse = sum(e**2 for e in temp_errors) / len(temp_errors)
                metrics['temperature']['mae'] += mae
                metrics['temperature']['mse'] += mse

            # Calculate humidity metrics
            humidity_errors = []
            for hist in historical_forecasts:
                if i < len(hist['daily']):
                    hist_day = hist['daily'][i]
                    error = abs(current_day['humidity'] - hist_day['humidity'])
                    humidity_errors.append(error)
            
            if humidity_errors:
                mae = sum(humidity_errors) / len(humidity_errors)
                mse = sum(e**2 for e in humidity_errors) / len(humidity_errors)
                metrics['humidity']['mae'] += mae
                metrics['humidity']['mse'] += mse

            # Calculate precipitation accuracy
            current_rain = current_day['precipitation']['amount'] > 0
            for hist in historical_forecasts:
                if i < len(hist['daily']):
                    hist_day = hist['daily'][i]
                    hist_rain = hist_day['precipitation']['amount'] > 0
                    
                    if current_rain and not hist_rain:
                        metrics['precipitation']['false_negatives'] += 1
                    elif not current_rain and hist_rain:
                        metrics['precipitation']['false_positives'] += 1

        # Calculate averages
        num_days = len(current_forecast['daily'])
        if num_days > 0:
            metrics['temperature']['mae'] /= num_days
            metrics['temperature']['mse'] /= num_days
            metrics['temperature']['rmse'] = metrics['temperature']['mse'] ** 0.5
            
            metrics['humidity']['mae'] /= num_days
            metrics['humidity']['mse'] /= num_days
            metrics['humidity']['rmse'] = metrics['humidity']['mse'] ** 0.5

        # Calculate precipitation accuracy
        total_predictions = len(historical_forecasts) * num_days
        if total_predictions > 0:
            metrics['precipitation']['accuracy'] = (
                1 - (metrics['precipitation']['false_positives'] + 
                metrics['precipitation']['false_negatives']) / total_predictions
            )

        return metrics

    def get_forecast_trends(self, lat: float, lon: float, days: int = 30) -> Dict:
        """Get trends in weather forecasts over time"""
        try:
            forecast_history = self.get_forecast_history(lat, lon, days)
            return self._analyze_forecast_trends(forecast_history)

        except Exception as e:
            self.logger.error(f"Error getting forecast trends: {str(e)}")
            raise

    def _analyze_forecast_trends(self, forecast_history: Dict) -> Dict:
        """Analyze trends in weather forecasts"""
        trends = {
            'temperature': {
                'overall_trend': 'stable',
                'daily_trends': []
            },
            'humidity': {
                'overall_trend': 'stable',
                'daily_trends': []
            },
            'precipitation': {
                'overall_trend': 'stable',
                'daily_trends': []
            }
        }

        # Analyze temperature trends
        temp_changes = []
        for i in range(1, len(forecast_history['historical_forecasts'])):
            current = forecast_history['historical_forecasts'][i]['summary']['temperature']['avg']
            previous = forecast_history['historical_forecasts'][i-1]['summary']['temperature']['avg']
            change = current - previous
            temp_changes.append(change)
            
            if change > 2:  # More than 2°C change
                trends['temperature']['daily_trends'].append('increasing')
            elif change < -2:
                trends['temperature']['daily_trends'].append('decreasing')
            else:
                trends['temperature']['daily_trends'].append('stable')

        # Determine overall temperature trend
        if sum(1 for t in trends['temperature']['daily_trends'] if t == 'increasing') > len(trends['temperature']['daily_trends']) * 0.6:
            trends['temperature']['overall_trend'] = 'increasing'
        elif sum(1 for t in trends['temperature']['daily_trends'] if t == 'decreasing') > len(trends['temperature']['daily_trends']) * 0.6:
            trends['temperature']['overall_trend'] = 'decreasing'

        # Analyze humidity trends
        humidity_changes = []
        for i in range(1, len(forecast_history['historical_forecasts'])):
            current = forecast_history['historical_forecasts'][i]['summary']['humidity']['avg']
            previous = forecast_history['historical_forecasts'][i-1]['summary']['humidity']['avg']
            change = current - previous
            humidity_changes.append(change)
            
            if change > 10:  # More than 10% change
                trends['humidity']['daily_trends'].append('increasing')
            elif change < -10:
                trends['humidity']['daily_trends'].append('decreasing')
            else:
                trends['humidity']['daily_trends'].append('stable')

        # Determine overall humidity trend
        if sum(1 for t in trends['humidity']['daily_trends'] if t == 'increasing') > len(trends['humidity']['daily_trends']) * 0.6:
            trends['humidity']['overall_trend'] = 'increasing'
        elif sum(1 for t in trends['humidity']['daily_trends'] if t == 'decreasing') > len(trends['humidity']['daily_trends']) * 0.6:
            trends['humidity']['overall_trend'] = 'decreasing'

        # Analyze precipitation trends
        for i in range(1, len(forecast_history['historical_forecasts'])):
            current = forecast_history['historical_forecasts'][i]['summary']['precipitation']['total']
            previous = forecast_history['historical_forecasts'][i-1]['summary']['precipitation']['total']
            
            if current > 0 and previous == 0:
                trends['precipitation']['daily_trends'].append('increasing')
            elif current == 0 and previous > 0:
                trends['precipitation']['daily_trends'].append('decreasing')
            else:
                trends['precipitation']['daily_trends'].append('stable')

        # Determine overall precipitation trend
        if sum(1 for t in trends['precipitation']['daily_trends'] if t == 'increasing') > len(trends['precipitation']['daily_trends']) * 0.6:
            trends['precipitation']['overall_trend'] = 'increasing'
        elif sum(1 for t in trends['precipitation']['daily_trends'] if t == 'decreasing') > len(trends['precipitation']['daily_trends']) * 0.6:
            trends['precipitation']['overall_trend'] = 'decreasing'

        return trends
