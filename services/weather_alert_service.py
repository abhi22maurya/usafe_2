import requests
import json
from datetime import datetime
from config import WEATHER_CONFIG, ALERT_CONFIG
import logging
from typing import Dict, List, Optional

class WeatherAlertService:
    def __init__(self):
        self.weather_api_key = WEATHER_CONFIG['api_key']
        self.alert_api_key = ALERT_CONFIG['api_key']
        self.weather_base_url = WEATHER_CONFIG['base_url']
        self.alert_base_url = ALERT_CONFIG['base_url']
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='logs/weather_alert_service.log'
        )
        self.logger = logging.getLogger(__name__)

    def get_weather_alerts(self, lat: float, lon: float) -> List[Dict]:
        """Get weather alerts for a specific location"""
        try:
            url = f"{self.weather_base_url}/onecall"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.weather_api_key,
                'exclude': 'current,minutely,hourly,daily',
                'units': 'metric'
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'alerts' in data:
                return data['alerts']
            else:
                return []

        except requests.RequestException as e:
            self.logger.error(f"Weather alerts request failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error getting weather alerts: {str(e)}")
            raise

    def create_weather_alert(self, alert_data: Dict) -> Dict:
        """Create a new weather alert"""
        try:
            required_fields = ['title', 'description', 'severity', 'location', 'start_time', 'end_time']
            if not all(field in alert_data for field in required_fields):
                raise ValueError("Missing required fields in alert data")

            alert_data['created_at'] = datetime.now().isoformat()
            
            url = f"{self.alert_base_url}/weather"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.alert_api_key}'
            }

            response = requests.post(
                url,
                headers=headers,
                json=alert_data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            self.logger.error(f"Weather alert creation failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error creating weather alert: {str(e)}")
            raise

    def get_active_weather_alerts(self, location: str = None) -> List[Dict]:
        """Get active weather alerts with optional location filter"""
        try:
            url = f"{self.alert_base_url}/weather/active"
            params = {}
            
            if location:
                params['location'] = location

            response = requests.get(
                url,
                params=params,
                headers={'Authorization': f'Bearer {self.alert_api_key}'},
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            self.logger.error(f"Active weather alerts retrieval failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error retrieving active weather alerts: {str(e)}")
            raise

    def update_weather_alert_status(self, alert_id: str, status: str) -> Dict:
        """Update weather alert status"""
        try:
            valid_statuses = ['active', 'resolved', 'cancelled']
            if status not in valid_statuses:
                raise ValueError(f"Invalid status: {status}")

            url = f"{self.alert_base_url}/weather/{alert_id}/status"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.alert_api_key}'
            }

            response = requests.put(
                url,
                headers=headers,
                json={'status': status},
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            self.logger.error(f"Weather alert status update failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error updating weather alert status: {str(e)}")
            raise
