import requests
import json
from datetime import datetime, timedelta
from config import WEATHER_CONFIG, ALERT_CONFIG
import logging
from typing import Dict, List, Optional

class WeatherAlertForecastService:
    def __init__(self):
        self.weather_api_key = WEATHER_CONFIG['api_key']
        self.weather_base_url = WEATHER_CONFIG['base_url']
        self.alert_api_key = ALERT_CONFIG['api_key']
        self.alert_base_url = ALERT_CONFIG['base_url']
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='logs/weather_alert_forecast_service.log'
        )
        self.logger = logging.getLogger(__name__)

    def get_alert_forecast(self, lat: float, lon: float) -> Dict:
        """Get forecast of weather alerts for a location"""
        try:
            # Get current weather conditions
            current_weather = self._get_current_weather(lat, lon)
            
            # Get weather forecast
            forecast = self._get_weather_forecast(lat, lon)
            
            # Analyze forecast for potential alerts
            alert_forecast = self._analyze_forecast_for_alerts(forecast)
            
            return {
                'current_weather': current_weather,
                'forecast': forecast,
                'alert_forecast': alert_forecast,
                'recommendations': self._generate_recommendations(alert_forecast)
            }

        except Exception as e:
            self.logger.error(f"Error getting alert forecast: {str(e)}")
            raise

    def _get_current_weather(self, lat: float, lon: float) -> Dict:
        """Get current weather data"""
        url = f"{self.weather_base_url}/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.weather_api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            'temperature': {
                'min': data['main']['temp_min'],
                'max': data['main']['temp_max'],
                'avg': data['main']['temp']
            },
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'wind_direction': data['wind']['deg'],
            'pressure': data['main']['pressure'],
            'description': data['weather'][0]['description'],
            'icon': data['weather'][0]['icon'],
            'precipitation': data.get('rain', {}).get('1h', 0.0)
        }

    def _get_weather_forecast(self, lat: float, lon: float) -> Dict:
        """Get weather forecast data"""
        url = f"{self.weather_base_url}/onecall"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.weather_api_key,
            'exclude': 'current,minutely,hourly,alerts',
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            'daily': data['daily'][:7]  # Get next 7 days
        }

    def _analyze_forecast_for_alerts(self, forecast: Dict) -> List[Dict]:
        """Analyze forecast data for potential alerts"""
        alerts = []
        
        for day in forecast['daily']:
            # Check for extreme temperature conditions
            if day['temp']['min'] < -10 or day['temp']['max'] > 40:
                alerts.append({
                    'type': 'temperature',
                    'severity': 'high',
                    'description': f"Extreme temperature conditions expected on {datetime.fromtimestamp(day['dt']).strftime('%Y-%m-%d')}",
                    'date': datetime.fromtimestamp(day['dt']).isoformat()
                })
            
            # Check for heavy precipitation
            if day.get('rain', {}).get('1h', 0.0) > 20:  # More than 20mm of rain
                alerts.append({
                    'type': 'rain',
                    'severity': 'high',
                    'description': f"Heavy rainfall expected on {datetime.fromtimestamp(day['dt']).strftime('%Y-%m-%d')}",
                    'date': datetime.fromtimestamp(day['dt']).isoformat()
                })
            
            # Check for high wind speeds
            if day['wind_speed'] > 30:  # More than 30 m/s
                alerts.append({
                    'type': 'wind',
                    'severity': 'high',
                    'description': f"Strong winds expected on {datetime.fromtimestamp(day['dt']).strftime('%Y-%m-%d')}",
                    'date': datetime.fromtimestamp(day['dt']).isoformat()
                })
            
            # Check for low pressure (potential storms)
            if day['pressure'] < 980:  # Below 980 hPa
                alerts.append({
                    'type': 'pressure',
                    'severity': 'high',
                    'description': f"Low pressure system expected on {datetime.fromtimestamp(day['dt']).strftime('%Y-%m-%d')}",
                    'date': datetime.fromtimestamp(day['dt']).isoformat()
                })
        
        return alerts

    def _generate_recommendations(self, alerts: List[Dict]) -> List[str]:
        """Generate recommendations based on forecasted alerts"""
        recommendations = []
        
        if not alerts:
            recommendations.append("No severe weather conditions expected in the forecast.")
            recommendations.append("Current conditions are generally safe.")
            return recommendations

        # Group alerts by type
        alert_types = {}
        for alert in alerts:
            if alert['type'] not in alert_types:
                alert_types[alert['type']] = []
            alert_types[alert['type']].append(alert)

        # Generate recommendations for each alert type
        for alert_type, alerts in alert_types.items():
            if alert_type == 'temperature':
                recommendations.append("Prepare for extreme temperature conditions:")
                recommendations.append("- Stay hydrated")
                recommendations.append("- Dress appropriately for the weather")
                recommendations.append("- Monitor local weather updates")
            
            elif alert_type == 'rain':
                recommendations.append("Prepare for heavy rainfall:")
                recommendations.append("- Secure outdoor items")
                recommendations.append("- Avoid low-lying areas")
                recommendations.append("- Monitor for potential flooding")
            
            elif alert_type == 'wind':
                recommendations.append("Prepare for strong winds:")
                recommendations.append("- Secure loose objects")
                recommendations.append("- Stay indoors during peak winds")
                recommendations.append("- Be cautious of falling objects")
            
            elif alert_type == 'pressure':
                recommendations.append("Prepare for potential storm conditions:")
                recommendations.append("- Stay informed about weather updates")
                recommendations.append("- Have emergency supplies ready")
                recommendations.append("- Follow local safety guidelines")

        # General recommendations
        recommendations.append("Stay informed about local weather updates.")
        recommendations.append("Follow recommended safety measures.")
        recommendations.append("Have emergency supplies ready.")

        return recommendations

    def get_alert_forecast_history(self, lat: float, lon: float, days: int = 30) -> Dict:
        """Get history of alert forecasts for a location"""
        try:
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                raise ValueError("Invalid coordinates")

            if days < 1 or days > 90:
                raise ValueError("Days must be between 1 and 90")

            # Get current alert forecast
            current_forecast = self.get_alert_forecast(lat, lon)
            
            # Get historical alert forecasts
            historical_forecasts = []
            for i in range(days):
                date = datetime.now() - timedelta(days=i)
                forecast = self._get_historical_alert_forecast(lat, lon, date)
                historical_forecasts.append(forecast)

            return {
                'current_forecast': current_forecast,
                'historical_forecasts': historical_forecasts,
                'accuracy_metrics': self._calculate_accuracy_metrics(
                    current_forecast,
                    historical_forecasts
                )
            }

        except Exception as e:
            self.logger.error(f"Error getting alert forecast history: {str(e)}")
            raise

    def _get_historical_alert_forecast(self, lat: float, lon: float, date: datetime) -> Dict:
        """Get historical alert forecast for a specific date"""
        weather_data = self._get_historical_weather(lat, lon, date)
        alerts = self._analyze_forecast_for_alerts(weather_data)
        
        return {
            'date': date.isoformat(),
            'weather': weather_data,
            'alerts': alerts,
            'recommendations': self._generate_recommendations(alerts)
        }

    def _get_historical_weather(self, lat: float, lon: float, date: datetime) -> Dict:
        """Get historical weather data for a specific date"""
        url = f"{self.weather_base_url}/data/2.5/onecall/timemachine"
        
        # Convert date to timestamp
        timestamp = int(date.timestamp())
        
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.weather_api_key,
            'dt': timestamp,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            'daily': [data['current']]  # Convert current data to daily format
        }

    def _calculate_accuracy_metrics(self, current_forecast: Dict, historical_forecasts: List[Dict]) -> Dict:
        """Calculate accuracy metrics for alert forecasts"""
        metrics = {
            'alert_accuracy': 0.0,
            'false_positives': 0,
            'false_negatives': 0,
            'total_predictions': 0
        }

        # Calculate metrics for each day
        for hist in historical_forecasts:
            if 'alerts' in hist and 'alerts' in current_forecast:
                current_alerts = set(a['type'] for a in current_forecast['alerts'])
                hist_alerts = set(a['type'] for a in hist['alerts'])
                
                # Calculate accuracy
                correct_predictions = len(current_alerts.intersection(hist_alerts))
                total_alerts = len(current_alerts.union(hist_alerts))
                
                if total_alerts > 0:
                    metrics['alert_accuracy'] += correct_predictions / total_alerts
                    
                # Calculate false positives and negatives
                false_positives = len(hist_alerts - current_alerts)
                false_negatives = len(current_alerts - hist_alerts)
                
                metrics['false_positives'] += false_positives
                metrics['false_negatives'] += false_negatives
                metrics['total_predictions'] += 1

        # Calculate averages
        if metrics['total_predictions'] > 0:
            metrics['alert_accuracy'] /= metrics['total_predictions']

        return metrics
