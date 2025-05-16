import psycopg2
import os
import logging
from dotenv import load_dotenv

def setup_database():
    try:
        # Load environment variables
        load_dotenv()
        
        # Get database name
        db_name = os.getenv('DB_NAME')
        if not db_name:
            raise ValueError("DB_NAME environment variable is not set")
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=db_name,
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        cursor = conn.cursor()
        
        # Enable PostGIS extension
        cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis")
        
        # Create resources table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id SERIAL PRIMARY KEY,
                type VARCHAR(50) NOT NULL,
                quantity INTEGER NOT NULL,
                status VARCHAR(20) NOT NULL,
                location GEOMETRY(POINT, 4326) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create response_teams table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS response_teams (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                type VARCHAR(50) NOT NULL,
                status VARCHAR(20) NOT NULL,
                capacity INTEGER NOT NULL,
                members INTEGER NOT NULL,
                response_time INTEGER NOT NULL,
                location GEOMETRY(POINT, 4326) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create incidents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id SERIAL PRIMARY KEY,
                type VARCHAR(50) NOT NULL,
                severity INTEGER NOT NULL,
                status VARCHAR(20) NOT NULL,
                description TEXT,
                location GEOMETRY(POINT, 4326) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create weather_alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather_alerts (
                id SERIAL PRIMARY KEY,
                type VARCHAR(50) NOT NULL,
                severity INTEGER NOT NULL,
                description TEXT,
                location GEOMETRY(POINT, 4326) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create spatial indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_resources_location 
            ON resources USING GIST (location)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_response_teams_location 
            ON response_teams USING GIST (location)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_incidents_location 
            ON incidents USING GIST (location)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_weather_alerts_location 
            ON weather_alerts USING GIST (location)
        """)
        
        # Commit changes
        conn.commit()
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("Database tables created successfully!")
        
    except Exception as e:
        logging.error(f"Error setting up database: {str(e)}")
        raise

if __name__ == "__main__":
    setup_database() 