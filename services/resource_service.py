import psycopg2
import os
import logging

class ResourceService:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD')
        }
        
    def get_nearby_resources(self, lat, lon, radius=50000):
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id,
                    type,
                    quantity,
                    status,
                    ST_Distance(
                        location,
                        ST_SetSRID(ST_MakePoint(%s, %s), 4326)
                    ) as distance
                FROM resources 
                WHERE ST_DWithin(
                    location,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                    %s
                )
                ORDER BY distance
            """, (lon, lat, lon, lat, radius))
            
            resources = []
            for row in cursor.fetchall():
                resources.append({
                    'id': row[0],
                    'type': row[1],
                    'quantity': row[2],
                    'status': row[3],
                    'distance': row[4]
                })
            
            cursor.close()
            conn.close()
            
            return resources
            
        except Exception as e:
            logging.error(f"Error getting nearby resources: {str(e)}")
            return [] 