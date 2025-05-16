import psycopg2
import os
import logging
from datetime import datetime, timedelta

class RiskAssessmentService:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD')
        }
        
    def assess_risk(self, lat, lon):
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Get recent incidents
            cursor.execute("""
                SELECT type, severity, timestamp 
                FROM incidents 
                WHERE ST_DWithin(
                    location,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                    50000
                )
                AND timestamp >= NOW() - INTERVAL '30 days'
            """, (lon, lat))
            recent_incidents = cursor.fetchall()
            
            # Get weather alerts
            cursor.execute("""
                SELECT type, severity, timestamp 
                FROM weather_alerts 
                WHERE ST_DWithin(
                    location,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                    50000
                )
                AND timestamp >= NOW() - INTERVAL '7 days'
            """, (lon, lat))
            weather_alerts = cursor.fetchall()
            
            # Calculate risk score
            risk_score = 0
            threats = set()
            
            # Add incident risk
            for incident in recent_incidents:
                risk_score += incident[1] * 10  # severity * 10
                threats.add(incident[0])
            
            # Add weather alert risk
            for alert in weather_alerts:
                risk_score += alert[1] * 5  # severity * 5
                threats.add(f"Weather: {alert[0]}")
            
            # Determine risk level
            if risk_score >= 100:
                risk_level = "Critical"
            elif risk_score >= 70:
                risk_level = "High"
            elif risk_score >= 40:
                risk_level = "Medium"
            else:
                risk_level = "Low"
            
            # Generate recommendations
            recommendations = []
            if "Flood" in threats:
                recommendations.append("Monitor water levels and prepare evacuation routes")
            if "Landslide" in threats:
                recommendations.append("Check slope stability and prepare emergency shelters")
            if "Earthquake" in threats:
                recommendations.append("Ensure emergency supplies and evacuation plans are ready")
            if "Weather: Heavy Rain" in threats:
                recommendations.append("Prepare for potential flooding and landslides")
            
            cursor.close()
            conn.close()
            
            return {
                'risk_level': risk_level,
                'risk_score': risk_score,
                'threats': list(threats),
                'recommendations': recommendations
            }
            
        except Exception as e:
            logging.error(f"Error assessing risk: {str(e)}")
            return {
                'risk_level': 'Unknown',
                'risk_score': 0,
                'threats': [],
                'recommendations': ['Unable to assess risk at this time']
            } 