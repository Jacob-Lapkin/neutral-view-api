import os

from dotenv import load_dotenv

db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

class Config:
    """
    custom config parent class for api
    """
    SECRET_KEY = "your_random_secret_key"
    JWT_SECRET_KEY = "your_jwt_secret_key"
    DEBUG = True
    VERSION = "v1"
    GOOGLE_CLIENT_ID = GOOGLE_CLIENT_ID
    GOOGLE_CLIENT_SECRET = GOOGLE_CLIENT_SECRET
    REACT_APP_URL = os.getenv("REACT_APP_URL", "http://localhost:3000")  # Default if not set

class Development(Config):
    """
    custom config child class for development environment
    """
    DEBUG = True
    VERSION = 'v1'
    HOST = "127.0.0.1"
    MONGO_CLIENT = "mongodb://localhost:27017"
    # Specific Development React app URL if different from the default
    REACT_APP_URL = os.getenv("REACT_APP_DEVELOPMENT_URL", Config.REACT_APP_URL)

class Production(Config):
    """
    custom config child class for production environment
    """
    DEBUG = False
    VERSION = 'v1'
    HOST = "0.0.0.0"
    MONGO_CLIENT = f'mongodb+srv://{db_username}:{db_password}@cluster0.njun9ub.mongodb.net/?retryWrites=true&w=majority'
    # Production React app URL
    REACT_APP_URL = os.getenv("REACT_APP_PRODUCTION_URL")
