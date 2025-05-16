from twilio.rest import Client
from typing import Dict, List, Optional
import requests
import json
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER

class MobileService:
    def __init__(self):
        self.twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        self.twilio_phone = TWILIO_PHONE_NUMBER
        self.push_notifications = []

    def send_sms(self, phone_number: str, message: str) -> Dict:
        """Send SMS using Twilio"""
        try:
            message = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_phone,
                to=phone_number
            )
            return {
                'status': 'success',
                'message_id': message.sid,
                'to': message.to,
                'status_code': message.status
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def send_emergency_alert(self, phone_numbers: List[str], alert_data: Dict) -> Dict:
        """Send emergency alert to multiple phone numbers"""
        results = []
        message = self._format_emergency_message(alert_data)
        
        for phone in phone_numbers:
            result = self.send_sms(phone, message)
            results.append({
                'phone': phone,
                'status': result['status'],
                'message_id': result.get('message_id'),
                'error': result.get('error')
            })
        
        return {
            'total_sent': len(phone_numbers),
            'results': results
        }

    def send_weather_alert(self, phone_numbers: List[str], weather_data: Dict) -> Dict:
        """Send weather alert to multiple phone numbers"""
        results = []
        message = self._format_weather_message(weather_data)
        
        for phone in phone_numbers:
            result = self.send_sms(phone, message)
            results.append({
                'phone': phone,
                'status': result['status'],
                'message_id': result.get('message_id'),
                'error': result.get('error')
            })
        
        return {
            'total_sent': len(phone_numbers),
            'results': results
        }

    def send_evacuation_alert(self, phone_numbers: List[str], evacuation_data: Dict) -> Dict:
        """Send evacuation alert to multiple phone numbers"""
        results = []
        message = self._format_evacuation_message(evacuation_data)
        
        for phone in phone_numbers:
            result = self.send_sms(phone, message)
            results.append({
                'phone': phone,
                'status': result['status'],
                'message_id': result.get('message_id'),
                'error': result.get('error')
            })
        
        return {
            'total_sent': len(phone_numbers),
            'results': results
        }

    def add_push_notification(self, user_id: str, title: str, message: str, data: Dict = None) -> Dict:
        """Add a push notification to the queue"""
        notification = {
            'user_id': user_id,
            'title': title,
            'message': message,
            'data': data or {},
            'timestamp': datetime.now().isoformat(),
            'status': 'pending'
        }
        self.push_notifications.append(notification)
        return notification

    def get_pending_notifications(self, user_id: str = None) -> List[Dict]:
        """Get pending push notifications"""
        if user_id:
            return [n for n in self.push_notifications 
                   if n['status'] == 'pending' and n['user_id'] == user_id]
        return [n for n in self.push_notifications if n['status'] == 'pending']

    def mark_notification_sent(self, notification_id: int) -> bool:
        """Mark a notification as sent"""
        if 0 <= notification_id < len(self.push_notifications):
            self.push_notifications[notification_id]['status'] = 'sent'
            return True
        return False

    def _format_emergency_message(self, alert_data: Dict) -> str:
        """Format emergency alert message"""
        return f"""EMERGENCY ALERT
Type: {alert_data.get('type', 'Unknown')}
Location: {alert_data.get('location', 'Unknown')}
Severity: {alert_data.get('severity', 'Unknown')}
Description: {alert_data.get('description', 'No description provided')}
Please follow official instructions and stay safe."""

    def _format_weather_message(self, weather_data: Dict) -> str:
        """Format weather alert message"""
        return f"""WEATHER ALERT
Condition: {weather_data.get('condition', 'Unknown')}
Temperature: {weather_data.get('temperature', 'Unknown')}°C
Wind Speed: {weather_data.get('wind_speed', 'Unknown')} km/h
Alert: {weather_data.get('alert', 'No alert')}
Stay safe and follow weather updates."""

    def _format_evacuation_message(self, evacuation_data: Dict) -> str:
        """Format evacuation alert message"""
        return f"""EVACUATION ALERT
Zone: {evacuation_data.get('zone', 'Unknown')}
Shelter: {evacuation_data.get('shelter', 'Unknown')}
Route: {evacuation_data.get('route', 'Follow official instructions')}
Estimated Time: {evacuation_data.get('estimated_time', 'Unknown')} minutes
Please evacuate immediately and follow the designated route.""" 