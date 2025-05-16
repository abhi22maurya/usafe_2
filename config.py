import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'dbname': os.getenv('DB_NAME', 'uttarakhand_safe'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

# OpenWeatherMap Configuration
WEATHER_CONFIG = {
    'api_key': os.getenv('OPENWEATHER_API_KEY'),
    'base_url': 'https://api.openweathermap.org/data/2.5',
    'units': 'metric'
}

# Geocoding Configuration
GEOCODING_CONFIG = {
    'service': os.getenv('GEOCODING_SERVICE', 'nominatim'),
    'user_agent': os.getenv('NOMINATIM_USER_AGENT', 'uttarakhand_safe')
}

# Translation Configuration
TRANSLATION_CONFIG = {
    'base_url': os.getenv('TRANSLATE_API_URL', 'https://libretranslate.com/translate'),
    'api_key': os.getenv('TRANSLATE_API_KEY'),
    'supported_languages': ['en', 'hi', 'ur']  # English, Hindi, Urdu
}

# SMS Configuration
SMS_CONFIG = {
    'account_sid': os.getenv('TWILIO_ACCOUNT_SID'),
    'auth_token': os.getenv('TWILIO_AUTH_TOKEN'),
    'phone_number': os.getenv('TWILIO_PHONE_NUMBER'),
    'base_url': 'https://api.twilio.com/2010-04-01/Accounts'
}

# Alert Configuration
ALERT_CONFIG = {
    'api_key': os.getenv('ALERT_API_KEY'),
    'base_url': 'https://api.uttarakhand-safe.com/alerts'
}

# TensorFlow Hub Models
MODEL_CONFIG = {
    'image_recognition': os.getenv(
        'IMAGE_RECOGNITION_MODEL',
        'https://tfhub.dev/google/imagenet/mobilenet_v2_130_224/classification/4'
    ),
    'text_classification': os.getenv(
        'TEXT_CLASSIFICATION_MODEL',
        'https://tfhub.dev/google/universal-sentence-encoder/4'
    )
}

# Application Settings
APP_CONFIG = {
    'debug': os.getenv('DEBUG', 'True').lower() == 'true',
    'secret_key': os.getenv('SECRET_KEY', 'your_secret_key_here'),
    'allowed_hosts': os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
}

# Machine Learning Settings
ML_CONFIG = {
    'model_update_interval': int(os.getenv('MODEL_UPDATE_INTERVAL', 3600)),
    'prediction_confidence_threshold': float(os.getenv('PREDICTION_CONFIDENCE_THRESHOLD', 0.7)),
    'max_prediction_history': int(os.getenv('MAX_PREDICTION_HISTORY', 1000))
}

# Logging Configuration
LOG_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'file_path': os.getenv('LOG_FILE_PATH', 'logs/app.log')
}

# Create required directories
os.makedirs('logs', exist_ok=True)
os.makedirs('models', exist_ok=True)

# Validate required configurations
def validate_config():
    required_vars = [
        ('OPENWEATHER_API_KEY', WEATHER_CONFIG['api_key']),
        ('DB_NAME', DB_CONFIG['dbname']),
        ('SECRET_KEY', APP_CONFIG['secret_key'])
    ]
    
    missing_vars = [var for var, value in required_vars if not value]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Validate configuration on import
validate_config() 