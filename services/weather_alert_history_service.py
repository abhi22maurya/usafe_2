import requests
import json
from datetime import datetime, timedelta
from config import ALERT_CONFIG
import logging
from typing import Dict, List, Optional

class WeatherAlertHistoryService:
    def __init__(self):
        self.api_key = ALERT_CONFIG['api_key']
        self.base_url = ALERT_CONFIG['base_url']
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='logs/weather_alert_history_service.log'
        )
        self.logger = logging.getLogger(__name__)

    def get_alert_history(self, location: str = None, start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """Get weather alert history with optional filters"""
        try:
            url = f"{self.base_url}/weather/alerts/history"
            params = {}
            
            if location:
                params['location'] = location
            if start_date:
                params['start_date'] = start_date.isoformat()
            if end_date:
                params['end_date'] = end_date.isoformat()

            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }

            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            self.logger.error(f"Alert history request failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error getting alert history: {str(e)}")
            raise

    def get_alert_statistics(self, location: str = None, time_range: str = '30d') -> Dict:
        """Get statistics about weather alerts"""
        try:
            url = f"{self.base_url}/weather/alerts/statistics"
            params = {
                'time_range': time_range
            }
            
            if location:
                params['location'] = location

            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }

            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            self.logger.error(f"Alert statistics request failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error getting alert statistics: {str(e)}")
            raise

    def get_alert_timeline(self, location: str = None, days: int = 30) -> List[Dict]:
        """Get timeline of weather alerts"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            alerts = self.get_alert_history(location, start_date, end_date)
            return self._process_timeline_data(alerts)

        except Exception as e:
            self.logger.error(f"Error getting alert timeline: {str(e)}")
            raise

    def _process_timeline_data(self, alerts: List[Dict]) -> List[Dict]:
        """Process and format the alert timeline data"""
        timeline = []
        
        for alert in alerts:
            timeline.append({
                'id': alert['id'],
                'title': alert['title'],
                'description': alert['description'],
                'severity': alert['severity'],
                'location': alert['location'],
                'start_time': alert['start_time'],
                'end_time': alert['end_time'],
                'status': alert['status'],
                'created_at': alert['created_at']
            })
        
        # Sort by creation time
        timeline.sort(key=lambda x: x['created_at'], reverse=True)
        return timeline

    def get_alert_types_distribution(self, location: str = None, time_range: str = '30d') -> Dict:
        """Get distribution of alert types"""
        try:
            url = f"{self.base_url}/weather/alerts/types"
            params = {
                'time_range': time_range
            }
            
            if location:
                params['location'] = location

            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }

            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            self.logger.error(f"Alert types request failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error getting alert types distribution: {str(e)}")
            raise

    def get_alert_severity_distribution(self, location: str = None, time_range: str = '30d') -> Dict:
        """Get distribution of alert severities"""
        try:
            url = f"{self.base_url}/weather/alerts/severity"
            params = {
                'time_range': time_range
            }
            
            if location:
                params['location'] = location

            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }

            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            self.logger.error(f"Alert severity request failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error getting alert severity distribution: {str(e)}")
            raise
