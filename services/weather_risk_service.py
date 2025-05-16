import requests
import json
from datetime import datetime, timedelta
from config import WEATHER_CONFIG, ML_CONFIG
import logging
import numpy as np
from typing import Dict, List, Optional

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
            # Extract relevant weather features
            features = self._extract_features(weather_data)
            
            # Normalize features
            normalized_features = self._normalize_features(features)
            
            # Calculate risk score using weighted sum
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
            
            # Apply sigmoid function to get score between 0 and 1
            risk_score = 1 / (1 + np.exp(-risk_score))
            
            return float(risk_score)
            
        except Exception as e:
            self.logger.error(f"Error calculating risk score: {str(e)}")
            raise

    def _extract_features(self, weather_data: Dict) -> Dict:
        """Extract relevant weather features for risk calculation"""
        return {
            'temperature': weather_data['temperature']['avg'],
            'humidity': weather_data['humidity'],
            'wind_speed': weather_data['wind_speed'],
            'precipitation': weather_data['precipitation']['amount'],
            'pressure': weather_data['pressure']
        }

    def _normalize_features(self, features: Dict) -> Dict:
        """Normalize weather features to a standard range"""
        # Temperature (°C) - normalize to 0-1 range
        features['temperature'] = (features['temperature'] + 20) / 60  # Assuming -20 to 40°C range
        
        # Humidity (%) - normalize to 0-1 range
        features['humidity'] = features['humidity'] / 100
        
        # Wind speed (m/s) - normalize to 0-1 range
        features['wind_speed'] = features['wind_speed'] / 50  # Assuming 0 to 50 m/s range
        
        # Precipitation (mm) - normalize to 0-1 range
        features['precipitation'] = min(features['precipitation'] / 100, 1)  # Capping at 100mm
        
        # Pressure (hPa) - normalize to 0-1 range
        features['pressure'] = (features['pressure'] - 950) / 100  # Assuming 950 to 1050 hPa range
        
        return features

    def get_risk_assessment(self, lat: float, lon: float) -> Dict:
        """Get comprehensive risk assessment for a location"""
        try:
            # Get current weather
            current_weather = self._get_current_weather(lat, lon)
            
            # Get weather forecast
            forecast = self._get_weather_forecast(lat, lon)
            
            # Calculate risk scores
            current_risk = self.calculate_risk_score(current_weather)
            forecast_risks = [self.calculate_risk_score(day) for day in forecast['daily']]
            
            # Analyze trends
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

    def _analyze_risk_trend(self, risk_scores: List[float]) -> str:
        """Analyze risk trend over the forecast period"""
        if len(risk_scores) < 2:
            return 'stable'
            
        # Calculate average change
        avg_change = sum(
            risk_scores[i] - risk_scores[i-1]
            for i in range(1, len(risk_scores))
        ) / (len(risk_scores) - 1)
        
        # Determine trend
        if avg_change > 0.1:  # More than 10% increase per day
            return 'increasing'
        elif avg_change < -0.1:  # More than 10% decrease per day
            return 'decreasing'
        else:
            return 'stable'

    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to risk level"""
        if risk_score < 0.3:
            return 'low'
        elif risk_score < 0.6:
            return 'moderate'
        else:
            return 'high'

    def _generate_recommendations(self, current_risk: float, trend: str) -> List[str]:
        """Generate recommendations based on risk assessment"""
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
