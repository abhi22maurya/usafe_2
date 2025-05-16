import unittest
import os
import time
from datetime import datetime, timedelta
from ai.weather_service import WeatherService
from dotenv import load_dotenv

class TestWeatherServiceIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test cases with actual API key"""
        load_dotenv()
        cls.api_key = os.getenv('OPENWEATHER_API_KEY')
        if not cls.api_key:
            raise unittest.SkipTest("OPENWEATHER_API_KEY not found in environment variables")
        
        cls.weather_service = WeatherService()
        # Uttarakhand coordinates
        cls.test_lat = 30.7333
        cls.test_lon = 79.0667
        # Small city coordinates for testing
        cls.small_city_lat = 30.3165
        cls.small_city_lon = 78.0322  # Dehradun

    def test_current_weather_integration(self):
        """Test getting current weather with actual API call"""
        # Add delay to respect rate limits
        time.sleep(1)
        
        result = self.weather_service.get_current_weather(self.test_lat, self.test_lon)
        
        # Verify basic structure
        self.assertIsInstance(result, dict)
        self.assertIn('temperature', result)
        self.assertIn('humidity', result)
        self.assertIn('pressure', result)
        self.assertIn('wind_speed', result)
        self.assertIn('description', result)
        
        # Verify data types
        self.assertIsInstance(result['temperature'], (int, float))
        self.assertIsInstance(result['humidity'], int)
        self.assertIsInstance(result['pressure'], (int, float))
        self.assertIsInstance(result['wind_speed'], (int, float))
        self.assertIsInstance(result['description'], str)

    def test_weather_forecast_integration(self):
        """Test getting weather forecast with actual API call"""
        time.sleep(1)
        
        result = self.weather_service.get_weather_forecast(self.test_lat, self.test_lon, days=2)
        
        # Verify basic structure
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
        # Verify first forecast item
        first_forecast = result[0]
        self.assertIn('timestamp', first_forecast)
        self.assertIn('temperature', first_forecast)
        self.assertIn('description', first_forecast)
        
        # Verify timestamp format
        try:
            datetime.strptime(first_forecast['timestamp'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            self.fail("Invalid timestamp format")

    def test_weather_alerts_integration(self):
        """Test getting weather alerts with actual API call"""
        time.sleep(1)
        
        result = self.weather_service.get_weather_alerts(self.test_lat, self.test_lon)
        
        # Verify result is a list
        self.assertIsInstance(result, list)
        
        # If there are alerts, verify their structure
        if result:
            alert = result[0]
            self.assertIn('event', alert)
            self.assertIn('description', alert)
            self.assertIn('start', alert)
            self.assertIn('end', alert)
            self.assertIn('severity', alert)

    def test_rate_limiting_integration(self):
        """Test rate limiting with actual API calls"""
        # Make multiple requests quickly
        start_time = time.time()
        for _ in range(3):
            self.weather_service.get_current_weather(self.small_city_lat, self.small_city_lon)
            time.sleep(0.1)  # Small delay to ensure rate limiting is triggered
        
        end_time = time.time()
        
        # Verify that the requests took at least 2 seconds (rate limit should have kicked in)
        self.assertGreater(end_time - start_time, 2)

    def test_cache_integration(self):
        """Test caching with actual API calls"""
        # First request (should hit API)
        start_time = time.time()
        result1 = self.weather_service.get_current_weather(self.small_city_lat, self.small_city_lon)
        first_request_time = time.time() - start_time
        
        # Second request (should hit cache)
        start_time = time.time()
        result2 = self.weather_service.get_current_weather(self.small_city_lat, self.small_city_lon)
        second_request_time = time.time() - start_time
        
        # Verify results are identical
        self.assertEqual(result1, result2)
        
        # Verify cache was faster
        self.assertLess(second_request_time, first_request_time)

    def test_error_handling_integration(self):
        """Test error handling with actual API calls"""
        # Test with invalid coordinates
        with self.assertRaises(Exception):
            self.weather_service.get_current_weather(999, 999)
        
        # Test with invalid API key
        original_key = self.weather_service.api_key
        self.weather_service.api_key = "invalid_key"
        with self.assertRaises(Exception):
            self.weather_service.get_current_weather(self.test_lat, self.test_lon)
        self.weather_service.api_key = original_key

    def test_multiple_locations_integration(self):
        """Test getting weather for multiple locations"""
        locations = [
            (self.test_lat, self.test_lon),  # Uttarakhand
            (self.small_city_lat, self.small_city_lon),  # Dehradun
            (30.1290, 78.2676)  # Rishikesh
        ]
        
        results = []
        for lat, lon in locations:
            time.sleep(1)  # Respect rate limits
            result = self.weather_service.get_current_weather(lat, lon)
            results.append(result)
        
        # Verify all locations returned valid data
        for result in results:
            self.assertIsInstance(result, dict)
            self.assertIn('temperature', result)
            self.assertIn('location', result)
            self.assertIsInstance(result['temperature'], (int, float))

if __name__ == '__main__':
    unittest.main() 