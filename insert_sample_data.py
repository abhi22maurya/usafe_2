import psycopg2
import os
import logging
from datetime import datetime, timedelta

def insert_sample_data():
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        cursor = conn.cursor()
        
        # Insert sample resources
        cursor.execute("""
            INSERT INTO resources (type, quantity, status, location) VALUES
            ('Medical Kit', 100, 'Available', ST_SetSRID(ST_MakePoint(78.2676, 30.0668), 4326)),
            ('Food Packets', 500, 'Available', ST_SetSRID(ST_MakePoint(78.1642, 29.9457), 4326)),
            ('Blankets', 200, 'Available', ST_SetSRID(ST_MakePoint(78.2676, 30.0668), 4326)),
            ('Water Bottles', 1000, 'Available', ST_SetSRID(ST_MakePoint(79.4543, 29.3919), 4326))
        """)
        
        # Insert sample response teams
        cursor.execute("""
            INSERT INTO response_teams (name, type, status, capacity, members, response_time, location) VALUES
            ('Medical Team 1', 'Medical', 'Available', 5, 5, 30, ST_SetSRID(ST_MakePoint(78.2676, 30.0668), 4326)),
            ('Rescue Team 1', 'Rescue', 'Available', 10, 8, 45, ST_SetSRID(ST_MakePoint(78.1642, 29.9457), 4326)),
            ('Food Distribution Team', 'Logistics', 'Available', 8, 6, 60, ST_SetSRID(ST_MakePoint(78.2676, 30.0668), 4326))
        """)
        
        # Insert sample incidents
        cursor.execute("""
            INSERT INTO incidents (type, severity, status, description, location, timestamp) VALUES
            ('Flood', 3, 'Active', 'River water level rising', ST_SetSRID(ST_MakePoint(78.1642, 29.9457), 4326), NOW() - INTERVAL '1 day'),
            ('Landslide', 2, 'Active', 'Road blocked due to landslide', ST_SetSRID(ST_MakePoint(78.2676, 30.0668), 4326), NOW() - INTERVAL '2 days'),
            ('Medical Emergency', 3, 'Active', 'Multiple injuries reported', ST_SetSRID(ST_MakePoint(79.4543, 29.3919), 4326), NOW() - INTERVAL '3 days')
        """)
        
        # Insert sample weather alerts
        cursor.execute("""
            INSERT INTO weather_alerts (type, severity, description, location, timestamp) VALUES
            ('Heavy Rain', 3, 'Heavy rainfall expected', ST_SetSRID(ST_MakePoint(78.2676, 30.0668), 4326), NOW() - INTERVAL '1 day'),
            ('Strong Winds', 2, 'Strong winds warning', ST_SetSRID(ST_MakePoint(78.1642, 29.9457), 4326), NOW() - INTERVAL '2 days')
        """)
        
        # Commit changes
        conn.commit()
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("Sample data inserted successfully!")
        
    except Exception as e:
        logging.error(f"Error inserting sample data: {str(e)}")
        raise

if __name__ == "__main__":
    insert_sample_data() 