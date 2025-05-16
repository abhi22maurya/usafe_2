import psycopg2
import os
import logging

class AnalyticsService:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD')
        }
        
    def get_quick_stats(self, lat, lon):
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Get active incidents
            cursor.execute("""
                SELECT COUNT(*) FROM incidents 
                WHERE status = 'active' 
                AND ST_DWithin(
                    location,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                    50000
                )
            """, (lon, lat))
            active_incidents = cursor.fetchone()[0]
            
            # Get available resources
            cursor.execute("""
                SELECT COUNT(*) FROM resources 
                WHERE status = 'available' 
                AND ST_DWithin(
                    location,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                    50000
                )
            """, (lon, lat))
            available_resources = cursor.fetchone()[0]
            
            # Get active teams
            cursor.execute("""
                SELECT COUNT(*) FROM response_teams 
                WHERE status = 'active' 
                AND ST_DWithin(
                    location,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                    50000
                )
            """, (lon, lat))
            active_teams = cursor.fetchone()[0]
            
            # Get response rate
            cursor.execute("""
                SELECT 
                    COUNT(*) FILTER (WHERE response_time <= 3600)::float / 
                    NULLIF(COUNT(*), 0) * 100
                FROM incidents 
                WHERE ST_DWithin(
                    location,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                    50000
                )
            """, (lon, lat))
            response_rate = cursor.fetchone()[0] or 0
            
            cursor.close()
            conn.close()
            
            return {
                'active_incidents': active_incidents,
                'available_resources': available_resources,
                'active_teams': active_teams,
                'response_rate': round(response_rate, 2)
            }
            
        except Exception as e:
            logging.error(f"Error getting quick stats: {str(e)}")
            return {
                'active_incidents': 0,
                'available_resources': 0,
                'active_teams': 0,
                'response_rate': 0
            } 