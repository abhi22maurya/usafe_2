import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, timedelta
import time
from ai.weather_service import WeatherService

class TestWeatherService(unittest.TestCase):
    def setUp(self):
        """Set up test cases"""
        self.weather_service = WeatherService()
        self.test_lat = 30.7333
        self.test_lon = 79.0667  # Coordinates for Uttarakhand

    def test_init(self):
        """Test WeatherService initialization"""
        self.assertIsNotNone(self.weather_service.api_key)
        self.assertEqual(self.weather_service.units, 'metric')
        self.assertEqual(self.weather_service.rate_limit, 60)
        self.assertEqual(self.weather_service.rate_window, 60)

    @patch('requests.get')
    def test_current_weather(self, mock_get):
        """Test getting current weather"""
        # Mock response data
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'main': {
                'temp': 20,
                'feels_like': 18,
                'humidity': 65,
                'pressure': 1012
            },
            'weather': [{'description': 'clear sky', 'icon': '01d'}],
            'wind': {'speed': 5, 'deg': 180},
            'name': 'Dehradun',
            'sys': {'country': 'IN'}
        }
        mock_get.return_value = mock_response

        # Test the method
        result = self.weather_service.get_current_weather(self.test_lat, self.test_lon)

        # Verify results
        self.assertEqual(result['temperature'], 20)
        self.assertEqual(result['location'], 'Dehradun')
        self.assertEqual(result['country'], 'IN')

    @patch('requests.get')
    def test_weather_forecast(self, mock_get):
        """Test getting weather forecast"""
        # Mock response data
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'list': [{
                'dt_txt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'main': {
                    'temp': 22,
                    'feels_like': 20,
                    'humidity': 70,
                    'pressure': 1010
                },
                'weather': [{'description': 'scattered clouds', 'icon': '03d'}],
                'wind': {'speed': 4, 'deg': 160},
                'pop': 0.2,
                'rain': {'3h': 0.5}
            }]
        }
        mock_get.return_value = mock_response

        # Test the method
        result = self.weather_service.get_weather_forecast(self.test_lat, self.test_lon, days=1)

        # Verify results
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['temperature'], 22)
        self.assertEqual(result[0]['precipitation_prob'], 20)  # 0.2 * 100
        self.assertEqual(result[0]['rain_volume'], 0.5)

    @patch('requests.get')
    def test_weather_alerts(self, mock_get):
        """Test getting weather alerts"""
        current_time = datetime.now()
        # Mock response data
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'alerts': [{
                'event': 'Heavy Rain Warning',
                'description': 'Severe rainfall expected',
                'start': int(current_time.timestamp()),
                'end': int((current_time + timedelta(hours=6)).timestamp()),
                'sender_name': 'IMD',
                'tags': ['rain', 'flood']
            }]
        }
        mock_get.return_value = mock_response

        # Test the method
        result = self.weather_service.get_weather_alerts(self.test_lat, self.test_lon)

        # Verify results
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['event'], 'Heavy Rain Warning')
        self.assertEqual(result[0]['severity'], 'high')  # Should be high due to "warning"
        self.assertEqual(result[0]['sender'], 'IMD')

    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        # Fill up the rate limit queue
        current_time = time.time()
        for _ in range(self.weather_service.rate_limit):
            self.weather_service.request_timestamps.append(current_time)

        # Measure time taken for next request
        start_time = time.time()
        self.weather_service._check_rate_limit()
        end_time = time.time()

        # Should have waited close to rate_window seconds
        self.assertGreater(end_time - start_time, 0.9 * self.weather_service.rate_window)

    def test_cache_management(self):
        """Test cache management functionality"""
        # Test cache addition and retrieval
        test_data = {'test': 'data'}
        self.weather_service._add_to_cache('test_key', test_data)
        
        # Test cache hit
        cached_data = self.weather_service._get_from_cache('test_key')
        self.assertEqual(cached_data, test_data)

        # Test cache statistics
        stats = self.weather_service.get_cache_stats()
        self.assertEqual(stats['total_entries'], 1)
        self.assertEqual(stats['active_entries'], 1)

        # Test cache duration update
        self.weather_service.update_cache_duration(1)  # 1 minute
        self.assertEqual(self.weather_service.cache_duration, timedelta(minutes=1))

        # Test cache clearing
        self.weather_service.clear_cache()
        self.assertEqual(len(self.weather_service.cache), 0)

    def test_error_handling(self):
        """Test error handling"""
        # Test invalid coordinates
        with self.assertRaises(ValueError):
            self.weather_service.get_current_weather("invalid", "coordinates")

        # Test invalid cache duration
        with self.assertRaises(ValueError):
            self.weather_service.update_cache_duration(0)

if __name__ == '__main__':
    unittest.main() 