import psycopg2
import os
import logging

class TeamService:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD')
        }
        
    def get_nearby_teams(self, lat, lon, radius=50000):
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id,
                    name,
                    type,
                    status,
                    capacity,
                    members,
                    response_time,
                    ST_Distance(
                        location,
                        ST_SetSRID(ST_MakePoint(%s, %s), 4326)
                    ) as distance
                FROM response_teams 
                WHERE ST_DWithin(
                    location,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                    %s
                )
                ORDER BY distance
            """, (lon, lat, lon, lat, radius))
            
            teams = []
            for row in cursor.fetchall():
                teams.append({
                    'id': row[0],
                    'name': row[1],
                    'type': row[2],
                    'status': row[3],
                    'capacity': row[4],
                    'members': row[5],
                    'response_time': row[6],
                    'distance': row[7]
                })
            
            cursor.close()
            conn.close()
            
            return teams
            
        except Exception as e:
            logging.error(f"Error getting nearby teams: {str(e)}")
            return [] 