from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from authlib.integrations.flask_client import OAuth
from configuration.config import Development, Production
from .routes.parent_bp import parent_bp

jwt = JWTManager()
cors = CORS()
oauth = OAuth()

def create_app(mode):
    """
    Takes in the configuration mode and returns app object for flask

    Paramaters:
    - mode (str) : the configuration type to run flask api in. 
    Returns:
    - app (object) : returns flask app object
    """
    app = Flask(__name__)

    # set environment
    if mode == "production":
        app.config.from_object(Production)
    else:
        app.config.from_object(Development)

    # init mongo clinet
    db = MongoClient(app.config['MONGO_CLIENT']).neutralview
    app.db = db

    # init flask extensions that contain init_app method
    jwt.init_app(app)
    cors.init_app(app)
    oauth.init_app(app)


    # Configure Google OAuth using Authlib
    google = oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        authorize_params=None,
        access_token_url='https://accounts.google.com/o/oauth2/token',
        access_token_params=None,
        refresh_token_url=None,
        redirect_to='google_login',
        client_kwargs={'scope': 'openid profile email'},
    )
    
    app.google = google

    # register blueprints
    app.register_blueprint(parent_bp, url_prefix="/v1")

    @app.route('/test', methods=["POST", "GET"])
    def test():
        return jsonify({"status":"success", "message":"Test fetched successfully"}), 200

    return app