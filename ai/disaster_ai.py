import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
import tensorflow_hub as hub
from datetime import datetime, timedelta
import joblib
import os
import logging

class DisasterAI:
    def __init__(self):
        self.risk_model = None
        self.resource_model = None
        self.image_model = None
        self.text_model = None
        self.scaler = StandardScaler()
        self.setup_logging()
        self.load_models()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='logs/disaster_ai.log'
        )
        self.logger = logging.getLogger(__name__)

    def load_models(self):
        """Load or initialize ML models"""
        try:
            # Load risk assessment model
            if os.path.exists('models/risk_model.joblib'):
                self.risk_model = joblib.load('models/risk_model.joblib')
            else:
                self.risk_model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )

            # Load resource prediction model
            if os.path.exists('models/resource_model.joblib'):
                self.resource_model = joblib.load('models/resource_model.joblib')
            else:
                self.resource_model = GradientBoostingRegressor(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=5,
                    random_state=42
                )

            # Load TensorFlow Hub models
            self.image_model = hub.load('https://tfhub.dev/google/imagenet/mobilenet_v2_130_224/classification/4')
            self.text_model = hub.load('https://tfhub.dev/google/universal-sentence-encoder/4')

        except Exception as e:
            self.logger.error(f"Error loading models: {str(e)}")
            raise

    def assess_risk(self, location_data, weather_data, historical_data):
        """
        Assess disaster risk for a given location
        
        Parameters:
        - location_data: dict with latitude, longitude, elevation, terrain_type
        - weather_data: dict with temperature, rainfall, wind_speed, humidity
        - historical_data: dict with past_incidents, vulnerability_index
        """
        try:
            # Prepare features
            features = np.array([[
                location_data['elevation'],
                weather_data['rainfall'],
                weather_data['temperature'],
                weather_data['wind_speed'],
                weather_data['humidity'],
                historical_data['vulnerability_index'],
                historical_data['past_incidents']
            ]])

            # Scale features
            features_scaled = self.scaler.fit_transform(features)

            # Get risk prediction
            risk_score = self.risk_model.predict_proba(features_scaled)[0]
            
            # Calculate confidence score
            confidence = np.max(risk_score)
            risk_level = ['Low', 'Medium', 'High', 'Critical'][np.argmax(risk_score)]

            return {
                'risk_level': risk_level,
                'confidence': confidence,
                'risk_factors': self._analyze_risk_factors(features[0], risk_score),
                'recommendations': self._generate_recommendations(risk_level, features[0])
            }

        except Exception as e:
            self.logger.error(f"Error in risk assessment: {str(e)}")
            raise

    def predict_resource_needs(self, incident_type, severity, population_affected, current_resources):
        """Predict resource requirements for an incident"""
        try:
            # Prepare features
            features = np.array([[
                self._encode_incident_type(incident_type),
                self._encode_severity(severity),
                population_affected,
                current_resources['medical'],
                current_resources['food'],
                current_resources['shelter'],
                current_resources['personnel']
            ]])

            # Scale features
            features_scaled = self.scaler.fit_transform(features)

            # Predict resources
            predictions = self.resource_model.predict(features_scaled)

            return {
                'medical_supplies': int(predictions[0]),
                'food_supplies': int(predictions[1]),
                'shelter_capacity': int(predictions[2]),
                'personnel_required': int(predictions[3]),
                'confidence': self.resource_model.score(features_scaled, predictions)
            }

        except Exception as e:
            self.logger.error(f"Error in resource prediction: {str(e)}")
            raise

    def analyze_image(self, image_data):
        """Analyze disaster-related images for damage assessment"""
        try:
            # Preprocess image
            img = tf.image.resize(image_data, (224, 224))
            img = tf.expand_dims(img, 0)

            # Get predictions
            predictions = self.image_model(img)
            scores = tf.nn.softmax(predictions[0])
            
            return {
                'damage_level': self._interpret_damage_level(scores),
                'confidence': float(tf.reduce_max(scores)),
                'features_detected': self._get_top_features(scores)
            }

        except Exception as e:
            self.logger.error(f"Error in image analysis: {str(e)}")
            raise

    def analyze_text_report(self, text):
        """Analyze text reports for emergency classification"""
        try:
            # Get text embeddings
            embeddings = self.text_model([text])
            
            # Classify emergency type
            emergency_type = self._classify_emergency(embeddings)
            
            return {
                'emergency_type': emergency_type['type'],
                'confidence': emergency_type['confidence'],
                'keywords': self._extract_keywords(text),
                'priority_level': self._determine_priority(text)
            }

        except Exception as e:
            self.logger.error(f"Error in text analysis: {str(e)}")
            raise

    def _analyze_risk_factors(self, features, risk_score):
        """Analyze contributing risk factors"""
        factor_weights = {
            'elevation': 0.15,
            'rainfall': 0.2,
            'temperature': 0.1,
            'wind_speed': 0.15,
            'humidity': 0.1,
            'vulnerability': 0.2,
            'historical': 0.1
        }
        
        risk_factors = {}
        for factor, weight in factor_weights.items():
            risk_factors[factor] = float(features[list(factor_weights.keys()).index(factor)] * weight)
        
        return risk_factors

    def _generate_recommendations(self, risk_level, features):
        """Generate safety recommendations based on risk assessment"""
        recommendations = []
        
        if risk_level in ['High', 'Critical']:
            recommendations.extend([
                "Activate emergency response teams",
                "Issue public safety alerts",
                "Prepare evacuation plans"
            ])
        
        if features[1] > 100:  # High rainfall
            recommendations.append("Monitor water levels and drainage systems")
        
        if features[3] > 50:  # High wind speed
            recommendations.append("Secure loose objects and structures")
        
        return recommendations

    def _encode_incident_type(self, incident_type):
        """Encode incident type to numerical value"""
        incident_types = {
            'flood': 1,
            'landslide': 2,
            'earthquake': 3,
            'fire': 4,
            'other': 0
        }
        return incident_types.get(incident_type.lower(), 0)

    def _encode_severity(self, severity):
        """Encode severity level to numerical value"""
        severity_levels = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        return severity_levels.get(severity.lower(), 1)

    def _interpret_damage_level(self, scores):
        """Interpret damage level from image analysis scores"""
        damage_levels = ['none', 'minor', 'moderate', 'severe', 'critical']
        return damage_levels[tf.argmax(scores)]

    def _get_top_features(self, scores, top_k=5):
        """Get top-k detected features from image analysis"""
        top_indices = tf.argsort(scores, direction='DESCENDING')[:top_k]
        return [f"Feature_{i}: {float(scores[i])}" for i in top_indices]

    def _classify_emergency(self, embeddings):
        """Classify emergency type from text embeddings"""
        # Implement emergency classification logic
        # This is a placeholder - you would typically have a trained classifier
        return {
            'type': 'flood',  # Replace with actual classification
            'confidence': 0.85
        }

    def _extract_keywords(self, text):
        """Extract important keywords from text"""
        # Implement keyword extraction
        # This is a placeholder
        return ['flood', 'rescue', 'urgent']

    def _determine_priority(self, text):
        """Determine priority level from text"""
        # Implement priority determination logic
        # This is a placeholder
        return 'high'

    def save_models(self):
        """Save ML models to disk"""
        try:
            if not os.path.exists('models'):
                os.makedirs('models')
            
            joblib.dump(self.risk_model, 'models/risk_model.joblib')
            joblib.dump(self.resource_model, 'models/resource_model.joblib')
            self.logger.info("Models saved successfully")
        
        except Exception as e:
            self.logger.error(f"Error saving models: {str(e)}")
            raise 