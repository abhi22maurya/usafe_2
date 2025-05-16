import os
import logging
from pathlib import Path

def setup_environment():
    try:
        # Create necessary directories
        os.makedirs('logs', exist_ok=True)
        os.makedirs('models', exist_ok=True)
        
        # Set environment variables
        os.environ['DB_HOST'] = 'localhost'
        os.environ['DB_PORT'] = '5432'
        os.environ['DB_NAME'] = 'uttarakhand_safe'
        os.environ['DB_USER'] = 'postgres'
        os.environ['DB_PASSWORD'] = 'postgres'
        os.environ['OPENWEATHER_API_KEY'] = 'e8e811877a24954d767d659b3aaaf3fc'
        os.environ['DEBUG'] = 'True'
        os.environ['SECRET_KEY'] = 'your-secret-key-here'
        os.environ['ALLOWED_HOSTS'] = 'localhost,127.0.0.1'
        
        # Create .env file
        env_content = """# Database configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=uttarakhand_safe
DB_USER=postgres
DB_PASSWORD=postgres

# OpenWeather API configuration
OPENWEATHER_API_KEY=e8e811877a24954d767d659b3aaaf3fc

# Application configuration
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("Environment setup completed successfully!")
        
    except Exception as e:
        logging.error(f"Error setting up environment: {str(e)}")
        raise

if __name__ == "__main__":
    setup_environment() 