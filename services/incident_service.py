import psycopg2
import os
import logging

class IncidentService:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD')
        }
        
    def get_incidents_by_location(self, lat, lon):
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id,
                    type,
                    severity,
                    status,
                    timestamp,
                    ST_Distance(
                        location,
                        ST_SetSRID(ST_MakePoint(%s, %s), 4326)
                    ) as distance
                FROM incidents 
                WHERE ST_DWithin(
                    location,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                    50000
                )
                ORDER BY timestamp DESC
            """, (lon, lat, lon, lat))
            
            incidents = []
            for row in cursor.fetchall():
                incidents.append({
                    'id': row[0],
                    'type': row[1],
                    'severity': row[2],
                    'status': row[3],
                    'timestamp': row[4],
                    'distance': row[5]
                })
            
            cursor.close()
            conn.close()
            
            return incidents
            
        except Exception as e:
            logging.error(f"Error getting incidents: {str(e)}")
            return [] 