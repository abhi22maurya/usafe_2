import requests
import json
from datetime import datetime
from config import ALERT_CONFIG, SMS_CONFIG
import logging
from typing import Dict, List, Optional

class AlertService:
    def __init__(self):
        self.api_key = ALERT_CONFIG['api_key']
        self.base_url = ALERT_CONFIG['base_url']
        self.sms_config = SMS_CONFIG
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='logs/alert_service.log'
        )
        self.logger = logging.getLogger(__name__)

    def create_alert(self, alert_data: Dict) -> Dict:
        """Create a new alert"""
        try:
            required_fields = ['title', 'description', 'severity', 'location']
            if not all(field in alert_data for field in required_fields):
                raise ValueError("Missing required fields in alert data")

            alert_data['created_at'] = datetime.now().isoformat()
            
            url = f"{self.base_url}/alerts"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
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
            self.logger.error(f"Alert creation failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error creating alert: {str(e)}")
            raise

    def send_sms_alert(self, phone_number: str, message: str) -> bool:
        """Send SMS alert"""
        try:
            url = f"{self.sms_config['base_url']}/send"
            params = {
                'api_key': self.sms_config['api_key'],
                'to': phone_number,
                'message': message
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return True

        except requests.RequestException as e:
            self.logger.error(f"SMS sending failed: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Error sending SMS: {str(e)}")
            return False

    def get_alerts(self, location: str = None, severity: str = None) -> List[Dict]:
        """Get alerts with optional filters"""
        try:
            url = f"{self.base_url}/alerts"
            params = {}
            
            if location:
                params['location'] = location
            if severity:
                params['severity'] = severity

            response = requests.get(
                url,
                params=params,
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            self.logger.error(f"Alert retrieval failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error retrieving alerts: {str(e)}")
            raise

    def update_alert_status(self, alert_id: str, status: str) -> Dict:
        """Update alert status"""
        try:
            valid_statuses = ['active', 'resolved', 'cancelled']
            if status not in valid_statuses:
                raise ValueError(f"Invalid status: {status}")

            url = f"{self.base_url}/alerts/{alert_id}/status"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
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
            self.logger.error(f"Alert status update failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error updating alert status: {str(e)}")
            raise
