from typing import Dict, List, Optional
import requests
import json
from datetime import datetime, timedelta
from config import WEATHER_CONFIG, ALERT_CONFIG, ML_CONFIG
import logging
import numpy as np

class WeatherRiskService:
    def __init__(self):
        self.weather_api_key = WEATHER_CONFIG['api_key']
        self.weather_base_url = WEATHER_CONFIG['base_url']
        self.ml_config = ML_CONFIG
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='logs/weather_risk_service.log'
        )
        self.logger = logging.getLogger(__name__)

    def calculate_risk_score(self, weather_data: Dict) -> float:
        """Calculate risk score based on weather conditions"""
        try:
            features = self._extract_features(weather_data)
            normalized_features = self._normalize_features(features)
            
            weights = {
                'temperature': 0.2,
                'humidity': 0.2,
                'wind_speed': 0.2,
                'precipitation': 0.3,
                'pressure': 0.1
            }
            
            risk_score = sum(
                normalized_features[feature] * weights[feature]
                for feature in weights
            )
            
            risk_score = 1 / (1 + np.exp(-risk_score))
            
            return float(risk_score)
            
        except Exception as e:
            self.logger.error(f"Error calculating risk score: {str(e)}")
            raise

    def get_risk_assessment(self, lat: float, lon: float) -> Dict:
        """Get comprehensive risk assessment for a location"""
        try:
            current_weather = self._get_current_weather(lat, lon)
            forecast = self._get_weather_forecast(lat, lon)
            
            current_risk = self.calculate_risk_score(current_weather)
            forecast_risks = [self.calculate_risk_score(day) for day in forecast['daily']]
            
            trend = self._analyze_risk_trend(forecast_risks)
            
            return {
                'current': {
                    'risk_score': current_risk,
                    'weather': current_weather,
                    'risk_level': self._get_risk_level(current_risk)
                },
                'forecast': {
                    'daily_risks': forecast_risks,
                    'trend': trend,
                    'weather': forecast
                },
                'recommendations': self._generate_recommendations(current_risk, trend)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting risk assessment: {str(e)}")
            raise

    # Helper methods
    def _extract_features(self, weather_data: Dict) -> Dict:
        return {
            'temperature': weather_data['temperature']['avg'],
            'humidity': weather_data['humidity'],
            'wind_speed': weather_data['wind_speed'],
            'precipitation': weather_data['precipitation']['amount'],
            'pressure': weather_data['pressure']
        }

    def _normalize_features(self, features: Dict) -> Dict:
        features['temperature'] = (features['temperature'] + 20) / 60
        features['humidity'] = features['humidity'] / 100
        features['wind_speed'] = features['wind_speed'] / 50
        features['precipitation'] = min(features['precipitation'] / 100, 1)
        features['pressure'] = (features['pressure'] - 950) / 100
        return features

    def _get_current_weather(self, lat: float, lon: float) -> Dict:
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
            'daily': data['daily'][:7]
        }

    def _analyze_risk_trend(self, risk_scores: List[float]) -> str:
        if len(risk_scores) < 2:
            return 'stable'
            
        avg_change = sum(
            risk_scores[i] - risk_scores[i-1]
            for i in range(1, len(risk_scores))
        ) / (len(risk_scores) - 1)
        
        if avg_change > 0.1:
            return 'increasing'
        elif avg_change < -0.1:
            return 'decreasing'
        else:
            return 'stable'

    def _get_risk_level(self, risk_score: float) -> str:
        if risk_score < 0.3:
            return 'low'
        elif risk_score < 0.6:
            return 'moderate'
        else:
            return 'high'

    def _generate_recommendations(self, current_risk: float, trend: str) -> List[str]:
        recommendations = []
        
        if current_risk < 0.3:
            recommendations.append("Current conditions are generally safe.")
        elif current_risk < 0.6:
            recommendations.append("Take standard precautions.")
            recommendations.append("Stay informed about local weather updates.")
        else:
            recommendations.append("High risk conditions detected.")
            recommendations.append("Take immediate safety measures.")
            recommendations.append("Stay indoors if possible.")

        if trend == 'increasing':
            recommendations.append("Risk is increasing. Stay alert.")
        elif trend == 'decreasing':
            recommendations.append("Risk is decreasing. Monitor conditions.")
        else:
            recommendations.append("Risk levels are stable.")

        return recommendations

class WeatherAlertRiskService:
    def __init__(self):
        self.api_key = ALERT_CONFIG['api_key']
        self.base_url = ALERT_CONFIG['base_url']
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='logs/weather_alert_risk_service.log'
        )
        self.logger = logging.getLogger(__name__)

    def get_alert_risk_assessment(self, lat: float, lon: float) -> Dict:
        """Get risk assessment based on weather alerts"""
        try:
            alerts = self.get_active_alerts(lat, lon)
            return self._analyze_alert_risk(alerts)
        except Exception as e:
            self.logger.error(f"Error getting alert risk assessment: {str(e)}")
            raise

    def get_active_alerts(self, lat: float, lon: float) -> List[Dict]:
        """Get active weather alerts for a location"""
        try:
            url = f"{self.base_url}/weather/alerts/active"
            params = {
                'lat': lat,
                'lon': lon
            }
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
        except Exception as e:
            self.logger.error(f"Error getting active alerts: {str(e)}")
            raise

    def _analyze_alert_risk(self, alerts: List[Dict]) -> Dict:
        """Analyze risk based on active alerts"""
        if not alerts:
            return {
                'risk_level': 'low',
                'alerts': [],
                'recommendations': ['No active alerts. Conditions are currently safe.']
            }

        risk_level = 'low'
        recommendations = []
        
        for alert in alerts:
            if alert['severity'] == 'severe':
                risk_level = 'high'
                recommendations.append(f"Severe alert: {alert['description']}")
            elif alert['severity'] == 'moderate' and risk_level != 'high':
                risk_level = 'moderate'
                recommendations.append(f"Moderate alert: {alert['description']}")

        recommendations.append("Stay informed about local weather updates.")
        recommendations.append("Follow recommended safety measures.")

        return {
            'risk_level': risk_level,
            'alerts': alerts,
            'recommendations': recommendations
        }
