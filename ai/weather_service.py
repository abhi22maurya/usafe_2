import requests
import json
from datetime import datetime, timedelta
from config import WEATHER_CONFIG
import logging
from collections import deque
import time

class WeatherService:
    def __init__(self):
        self.api_key = WEATHER_CONFIG['api_key']
        self.base_url = WEATHER_CONFIG['base_url']
        self.units = WEATHER_CONFIG['units']
        self.cache = {}
        self.cache_duration = timedelta(minutes=30)
        # Rate limiting - max 60 calls per minute
        self.rate_limit = 60
        self.rate_window = 60  # seconds
        self.request_timestamps = deque(maxlen=self.rate_limit)
        self.setup_logging()
        self.accuracy_metrics = {
            'temperature': [],
            'humidity': [],
            'wind_speed': [],
            'pressure': []
        }
        self.error_count = 0
        self.total_requests = 0

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='logs/weather_service.log'
        )
        self.logger = logging.getLogger(__name__)

    def _track_accuracy_metrics(self, weather_data):
        """Track accuracy metrics for weather data"""
        # Track temperature accuracy
        if 'temperature' in self.accuracy_metrics:
            self.accuracy_metrics['temperature'].append(weather_data['temperature'])
            if len(self.accuracy_metrics['temperature']) > 100:
                self.accuracy_metrics['temperature'].pop(0)

        # Track humidity accuracy
        if 'humidity' in self.accuracy_metrics:
            self.accuracy_metrics['humidity'].append(weather_data['humidity'])
            if len(self.accuracy_metrics['humidity']) > 100:
                self.accuracy_metrics['humidity'].pop(0)

        # Calculate accuracy statistics
        self._calculate_accuracy_stats()

    def _calculate_accuracy_stats(self):
        """Calculate accuracy statistics"""
        stats = {}
        for metric, values in self.accuracy_metrics.items():
            if values:
                avg = sum(values) / len(values)
                variance = sum((x - avg) ** 2 for x in values) / len(values)
                stats[metric] = {
                    'average': avg,
                    'variance': variance,
                    'count': len(values)
                }

        # Log accuracy statistics
        self.logger.info(f"Accuracy stats: {json.dumps(stats)}")

    def get_accuracy_report(self):
        """Get accuracy report"""
        if self.total_requests == 0:
            return {
                'error_rate': 0,
                'accuracy_stats': self._calculate_accuracy_stats()
            }

        error_rate = (self.error_count / self.total_requests) * 100
        return {
            'error_rate': error_rate,
            'accuracy_stats': self._calculate_accuracy_stats(),
            'total_requests': self.total_requests,
            'successful_requests': self.total_requests - self.error_count
        }

    def _check_rate_limit(self):
        """Implement rate limiting"""
        now = time.time()
        
        # Remove timestamps older than the window
        while self.request_timestamps and self.request_timestamps[0] < now - self.rate_window:
            self.request_timestamps.popleft()
        
        if len(self.request_timestamps) >= self.rate_limit:
            sleep_time = self.request_timestamps[0] + self.rate_window - now
            if sleep_time > 0:
                self.logger.warning(f"Rate limit reached. Waiting {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
        
        self.request_timestamps.append(now)

    def _make_api_request(self, url, params):
        """Make an API request with rate limiting and error handling"""
        self._check_rate_limit()
        
        try:
            response = requests.get(url, params=params, timeout=10)  # Add timeout
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            self.logger.error("Request timed out")
            raise TimeoutError("Weather API request timed out")
        except requests.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            raise

    def get_current_weather(self, lat, lon):
        """Get current weather data for a location with enhanced validation"""
        try:
            self.total_requests += 1
            
            # Validate input coordinates
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                raise ValueError("Invalid coordinates")

            cache_key = f"current_{lat}_{lon}"
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return cached_data

            url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': self.units
            }

            data = self._make_api_request(url, params)

            # Validate and clean the data
            try:
                weather_data = {
                    'temperature': float(data['main']['temp']),
                    'feels_like': float(data['main']['feels_like']),
                    'humidity': float(data['main']['humidity']),
                    'pressure': float(data['main']['pressure']),
                    'wind_speed': float(data['wind']['speed']),
                    'wind_direction': float(data['wind']['deg']),
                    'description': str(data['weather'][0]['description']),
                    'icon': str(data['weather'][0]['icon']),
                    'timestamp': datetime.now().isoformat(),
                    'location': str(data.get('name', 'Unknown')),
                    'country': str(data.get('sys', {}).get('country', 'Unknown'))
                }

                # Track accuracy metrics
                self._track_accuracy_metrics(weather_data)

            except (ValueError, KeyError, TypeError) as e:
                self.logger.error(f"Data validation error: {str(e)}")
                self.error_count += 1
                raise ValueError("Invalid or corrupted weather data")

            self._add_to_cache(cache_key, weather_data)
            return weather_data

        except (KeyError, IndexError) as e:
            self.logger.error(f"Error parsing weather data: {str(e)}")
            self.error_count += 1
            raise ValueError("Invalid weather data format received")
        except Exception as e:
            self.logger.error(f"Error getting current weather: {str(e)}")
            self.error_count += 1
            raise

    def get_weather_forecast(self, lat, lon, days=5):
        """Get weather forecast for a location"""
        try:
            cache_key = f"forecast_{lat}_{lon}_{days}"
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return cached_data

            url = f"{self.base_url}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': self.units
            }

            data = self._make_api_request(url, params)

            forecast_data = []
            for item in data['list']:
                forecast_data.append({
                    'timestamp': item['dt_txt'],
                    'temperature': item['main']['temp'],
                    'feels_like': item['main']['feels_like'],
                    'humidity': item['main']['humidity'],
                    'pressure': item['main']['pressure'],
                    'wind_speed': item['wind']['speed'],
                    'wind_direction': item['wind']['deg'],
                    'description': item['weather'][0]['description'],
                    'icon': item['weather'][0]['icon'],
                    'precipitation_prob': item.get('pop', 0) * 100,  # Convert to percentage
                    'rain_volume': item.get('rain', {}).get('3h', 0)  # Rain volume for 3 hours
                })

            # Filter to requested number of days
            current_date = datetime.now().date()
            filtered_forecast = [
                item for item in forecast_data 
                if (datetime.strptime(item['timestamp'], '%Y-%m-%d %H:%M:%S').date() - current_date).days < days
            ]

            self._add_to_cache(cache_key, filtered_forecast)
            return filtered_forecast

        except (KeyError, IndexError) as e:
            self.logger.error(f"Error parsing forecast data: {str(e)}")
            raise ValueError("Invalid forecast data format received")
        except Exception as e:
            self.logger.error(f"Error getting weather forecast: {str(e)}")
            raise

    def get_weather_alerts(self, lat, lon):
        """Get weather alerts for a location"""
        try:
            cache_key = f"alerts_{lat}_{lon}"
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return cached_data

            url = f"{self.base_url}/onecall"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': self.units,
                'exclude': 'current,minutely,hourly,daily'
            }

            data = self._make_api_request(url, params)

            alerts = []
            if 'alerts' in data:
                for alert in data['alerts']:
                    alerts.append({
                        'event': alert['event'],
                        'description': alert['description'],
                        'start': datetime.fromtimestamp(alert['start']).isoformat(),
                        'end': datetime.fromtimestamp(alert['end']).isoformat(),
                        'severity': self._determine_severity(alert),
                        'sender': alert.get('sender_name', 'Unknown'),
                        'tags': alert.get('tags', [])
                    })

            self._add_to_cache(cache_key, alerts)
            return alerts

        except (KeyError, ValueError) as e:
            self.logger.error(f"Error parsing alert data: {str(e)}")
            raise ValueError("Invalid alert data format received")
        except Exception as e:
            self.logger.error(f"Error getting weather alerts: {str(e)}")
            raise

    def _get_from_cache(self, key):
        """Get data from cache if not expired"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.cache_duration:
                self.logger.debug(f"Cache hit for key: {key}")
                return data
            else:
                self.logger.debug(f"Cache expired for key: {key}")
                del self.cache[key]
        return None

    def _add_to_cache(self, key, data):
        """Add data to cache with current timestamp"""
        self.logger.debug(f"Caching data for key: {key}")
        self.cache[key] = (data, datetime.now())
        self._cleanup_cache()

    def _cleanup_cache(self):
        """Remove expired entries from cache"""
        now = datetime.now()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if now - timestamp >= self.cache_duration
        ]
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self.logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

    def _determine_severity(self, alert):
        """Determine severity level of weather alert"""
        severity_keywords = {
            'high': ['severe', 'extreme', 'danger', 'warning', 'emergency', 'hurricane', 'tornado'],
            'medium': ['watch', 'advisory', 'caution', 'alert'],
            'low': ['statement', 'outlook', 'information', 'update']
        }

        event_lower = alert['event'].lower()
        description_lower = alert.get('description', '').lower()
        
        # Check both event and description for severity keywords
        for level, keywords in severity_keywords.items():
            if any(keyword in event_lower or keyword in description_lower for keyword in keywords):
                return level
        return 'low'  # Default severity

    def clear_cache(self):
        """Clear all cached weather data"""
        self.cache.clear()
        self.logger.info("Weather cache cleared")

    def get_cache_stats(self):
        """Get statistics about the cache"""
        now = datetime.now()
        total_entries = len(self.cache)
        expired_entries = sum(1 for _, timestamp in self.cache.values() if now - timestamp >= self.cache_duration)
        active_entries = total_entries - expired_entries
        
        return {
            'total_entries': total_entries,
            'active_entries': active_entries,
            'expired_entries': expired_entries,
            'cache_duration_minutes': self.cache_duration.total_seconds() / 60
        }

    def update_cache_duration(self, minutes):
        """Update the cache duration"""
        if minutes < 1:
            raise ValueError("Cache duration must be at least 1 minute")
        self.cache_duration = timedelta(minutes=minutes)
        self.logger.info(f"Cache duration updated to {minutes} minutes")
        self._cleanup_cache()  # Clean up any entries that would be expired under new duration 