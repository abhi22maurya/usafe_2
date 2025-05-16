#!/usr/bin/env python3
import os
import secrets
import getpass

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_urlsafe(32)

def get_user_input(prompt, default=None, password=False):
    """Get user input with optional default value"""
    if default:
        prompt = f"{prompt} [default: {default}]: "
    else:
        prompt = f"{prompt}: "
    
    if password:
        value = getpass.getpass(prompt)
    else:
        value = input(prompt)
    
    return value if value else default

def setup_api_keys():
    """Interactive setup for API keys and configuration"""
    print("Welcome to Uttarakhand Safe API Configuration Setup")
    print("================================================")
    print("\nThis script will help you set up the necessary API keys and configuration.")
    print("You can press Enter to skip any optional service.\n")

    config = {}

    # Database Configuration
    print("\n=== Database Configuration ===")
    config['DB_HOST'] = get_user_input("Database host", "localhost")
    config['DB_PORT'] = get_user_input("Database port", "5432")
    config['DB_NAME'] = get_user_input("Database name", "uttarakhand_safe")
    config['DB_USER'] = get_user_input("Database user", "postgres")
    config['DB_PASSWORD'] = get_user_input("Database password", password=True)

    # OpenWeatherMap Configuration
    print("\n=== OpenWeatherMap Configuration ===")
    print("Sign up at: https://home.openweathermap.org/users/sign_up")
    config['OPENWEATHER_API_KEY'] = get_user_input("OpenWeatherMap API Key")

    # Translation Service
    print("\n=== Translation Service Configuration ===")
    print("Options:")
    print("1. Use public LibreTranslate instance (rate limited)")
    print("2. Self-host LibreTranslate")
    translate_choice = get_user_input("Choose option", "1")
    if translate_choice == "2":
        config['TRANSLATE_API_URL'] = get_user_input("LibreTranslate API URL")
        config['TRANSLATE_API_KEY'] = get_user_input("LibreTranslate API Key")
    else:
        config['TRANSLATE_API_URL'] = "https://libretranslate.com/translate"

    # SMS Service (Twilio)
    print("\n=== SMS Service Configuration (Twilio) ===")
    print("Sign up at: https://www.twilio.com/try-twilio")
    config['TWILIO_ACCOUNT_SID'] = get_user_input("Twilio Account SID")
    config['TWILIO_AUTH_TOKEN'] = get_user_input("Twilio Auth Token")
    config['TWILIO_PHONE_NUMBER'] = get_user_input("Twilio Phone Number")

    # Application Settings
    print("\n=== Application Settings ===")
    config['DEBUG'] = get_user_input("Enable debug mode? (True/False)", "True")
    config['SECRET_KEY'] = get_user_input("Secret key", generate_secret_key())
    config['ALLOWED_HOSTS'] = get_user_input("Allowed hosts", "localhost,127.0.0.1")

    # Write configuration to .env file
    with open('.env', 'w') as f:
        for key, value in config.items():
            if value:
                f.write(f"{key}={value}\n")

    print("\nConfiguration has been saved to .env file.")
    print("\nNext steps:")
    print("1. Review the .env file and make any necessary adjustments")
    print("2. Run 'python setup_db.py' to initialize the database")
    print("3. Run 'python app.py' to start the application")

if __name__ == "__main__":
    setup_api_keys() 