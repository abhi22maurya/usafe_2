import requests
import json
from datetime import datetime, timedelta
from config import WEATHER_CONFIG, ML_CONFIG
import logging
from typing import Dict, List, Optional

class WeatherRiskHistoryService:
    def __init__(self):
        self.weather_api_key = WEATHER_CONFIG['api_key']
        self.weather_base_url = WEATHER_CONFIG['base_url']
        self.ml_config = ML_CONFIG
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='logs/weather_risk_history_service.log'
        )
        self.logger = logging.getLogger(__name__)

    def get_risk_history(self, lat: float, lon: float, days: int = 30) -> Dict:
        """Get historical risk assessments for a location"""
        try:
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                raise ValueError("Invalid coordinates")

            if days < 1 or days > 90:
                raise ValueError("Days must be between 1 and 90")

            # Get current risk assessment
            current_risk = self._get_current_risk(lat, lon)
            
            # Get historical risk assessments
            historical_risks = []
            for i in range(days):
                date = datetime.now() - timedelta(days=i)
                risk = self._get_historical_risk(lat, lon, date)
                historical_risks.append(risk)

            return {
                'current_risk': current_risk,
                'historical_risks': historical_risks,
                'trends': self._analyze_risk_trends(historical_risks)
            }

        except Exception as e:
            self.logger.error(f"Error getting risk history: {str(e)}")
            raise

    def _get_current_risk(self, lat: float, lon: float) -> Dict:
        """Get current risk assessment"""
        weather_data = self._get_current_weather(lat, lon)
        risk_score = self._calculate_risk_score(weather_data)
        
        return {
            'date': datetime.now().isoformat(),
            'risk_score': risk_score,
            'risk_level': self._get_risk_level(risk_score),
            'weather': weather_data
        }

    def _get_historical_risk(self, lat: float, lon: float, date: datetime) -> Dict:
        """Get historical risk assessment for a specific date"""
        weather_data = self._get_historical_weather(lat, lon, date)
        risk_score = self._calculate_risk_score(weather_data)
        
        return {
            'date': date.isoformat(),
            'risk_score': risk_score,
            'risk_level': self._get_risk_level(risk_score),
            'weather': weather_data
        }

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
            'temperature': {
                'min': data['current']['temp_min'],
                'max': data['current']['temp_max'],
                'avg': data['current']['temp']
            },
            'humidity': data['current']['humidity'],
            'wind_speed': data['current']['wind_speed'],
            'wind_direction': data['current']['wind_deg'],
            'pressure': data['current']['pressure'],
            'description': data['current']['weather'][0]['description'],
            'icon': data['current']['weather'][0]['icon'],
            'precipitation': data['current'].get('rain', {}).get('1h', 0.0)
        }

    def _calculate_risk_score(self, weather_data: Dict) -> float:
        """Calculate risk score based on weather conditions"""
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

    def _extract_features(self, weather_data: Dict) -> Dict:
        """Extract relevant weather features for risk calculation"""
        return {
            'temperature': weather_data['temperature']['avg'],
            'humidity': weather_data['humidity'],
            'wind_speed': weather_data['wind_speed'],
            'precipitation': weather_data['precipitation'],
            'pressure': weather_data['pressure']
        }

    def _normalize_features(self, features: Dict) -> Dict:
        """Normalize weather features to a standard range"""
        features['temperature'] = (features['temperature'] + 20) / 60
        features['humidity'] = features['humidity'] / 100
        features['wind_speed'] = features['wind_speed'] / 50
        features['precipitation'] = min(features['precipitation'] / 100, 1)
        features['pressure'] = (features['pressure'] - 950) / 100
        return features

    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to risk level"""
        if risk_score < 0.3:
            return 'low'
        elif risk_score < 0.6:
            return 'moderate'
        else:
            return 'high'

    def _analyze_risk_trends(self, historical_risks: List[Dict]) -> Dict:
        """Analyze trends in risk assessments"""
        if not historical_risks:
            return {
                'overall_trend': 'stable',
                'daily_trends': []
            }

        trends = []
        for i in range(1, len(historical_risks)):
            current = historical_risks[i]['risk_score']
            previous = historical_risks[i-1]['risk_score']
            change = current - previous
            
            if change > 0.1:  # More than 10% increase
                trends.append('increasing')
            elif change < -0.1:  # More than 10% decrease
                trends.append('decreasing')
            else:
                trends.append('stable')

        # Determine overall trend
        if sum(1 for t in trends if t == 'increasing') > len(trends) * 0.6:
            overall_trend = 'increasing'
        elif sum(1 for t in trends if t == 'decreasing') > len(trends) * 0.6:
            overall_trend = 'decreasing'
        else:
            overall_trend = 'stable'

        return {
            'overall_trend': overall_trend,
            'daily_trends': trends
        }

    def get_risk_statistics(self, lat: float, lon: float, days: int = 30) -> Dict:
        """Get statistics about risk assessments"""
        try:
            risk_history = self.get_risk_history(lat, lon, days)
            return self._calculate_risk_statistics(risk_history['historical_risks'])

        except Exception as e:
            self.logger.error(f"Error getting risk statistics: {str(e)}")
            raise

    def _calculate_risk_statistics(self, historical_risks: List[Dict]) -> Dict:
        """Calculate statistics about risk assessments"""
        if not historical_risks:
            return {
                'average_risk': 0.0,
                'risk_level_distribution': {
                    'low': 0,
                    'moderate': 0,
                    'high': 0
                },
                'trend_changes': {
                    'increasing': 0,
                    'decreasing': 0,
                    'stable': 0
                }
            }

        # Calculate average risk
        average_risk = sum(r['risk_score'] for r in historical_risks) / len(historical_risks)

        # Calculate risk level distribution
        risk_level_distribution = {
            'low': sum(1 for r in historical_risks if r['risk_level'] == 'low'),
            'moderate': sum(1 for r in historical_risks if r['risk_level'] == 'moderate'),
            'high': sum(1 for r in historical_risks if r['risk_level'] == 'high')
        }

        # Calculate trend changes
        trends = self._analyze_risk_trends(historical_risks)['daily_trends']
        trend_changes = {
            'increasing': sum(1 for t in trends if t == 'increasing'),
            'decreasing': sum(1 for t in trends if t == 'decreasing'),
            'stable': sum(1 for t in trends if t == 'stable')
        }

        return {
            'average_risk': average_risk,
            'risk_level_distribution': risk_level_distribution,
            'trend_changes': trend_changes
        }
