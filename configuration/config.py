from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = "alsknei993ksnsi3"
    JWT_SECRET_KEY = "askljjnedlkaj3"
    DEBUG = True
    VERSION = "v1"
    GOOGLE_CLIENT_ID = "changethislater"
    GOOGLE_CLIENT_SECRET = "changethislater"

class Development(Config):
    DEBUG = True
    VERSION = 'v1'
    HOST = "127.0.0.1"
    MONGO_CLIENT = "mongodb://localhost:27017"


class Production(Config):
    DEBUG = False
    VERSION = 'v1'
    HOST = "0.0.0.0"
    MONGO_CLIENT = "Fill this in later"
