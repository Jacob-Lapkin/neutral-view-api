# pylint: disable=broad-exception-caught
from datetime import datetime
from urllib.parse import urlencode

from authlib.integrations.flask_client import OAuthError
from flask import Blueprint, current_app, jsonify, redirect, request, url_for
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt_identity, jwt_required)
from requests.exceptions import HTTPError
from werkzeug.security import check_password_hash, generate_password_hash

auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route("/auth/register", methods=["POST"])
def register():
    try:
        # get db instance
        db = current_app.db

        # get registration data
        data = request.get_json()
        email = data.get("email", None)
        password = data.get("password", None)
        password_match = data.get("passwordMatch", None)

        # check if all required data is provided
        if not all([email, password, password_match]):
            return jsonify({"status": "error", "message": "Required registration information missing"}), 400

        # check if passwords match:
        if password != password_match:
            return jsonify({"status": "error", "message": "passwords do not match"}), 400

        # check if user exists in database
        user = db.users.find_one({
            "email":email
        })

        if user:
            return ({"status": "error", "message": "Email has already been registered"}), 400

        # create password hash
        hashed_password = generate_password_hash(password=password)

        new_user = {
            "profile": {
                "username": None,
                "email": email
            },
            "authentication": {
                "password": hashed_password,
                "profileCreation": "Registration",
                "accountStatus": "active",
                "lastLoginDate": datetime.now()
            }
        }

        # insert user into database
        new_user_inserted = db.users.insert_one(new_user)

        return jsonify({"status": "success", "messaage": f"successfully registered new user {new_user_inserted.inserted_id}"}), 201

    except Exception as error:
        return jsonify({"status": "error", "message": str(error)}), 500


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    try:
        db = current_app.db
        data = request.get_json()
        email = data.get("email", None)
        password = data.get("password", None)

        if not all([email, password]):
            return jsonify({"status": "error", "message": "Required login information missing"}), 400

        user = db.users.find_one({"profile.email": email})
        if user["authentication"]['profileCreation'] != "Registration":
            return jsonify({"status": "error", "message": "You have already registered your account using an auth provider. Please login with your auth provider"}), 400
        if not user or not check_password_hash(user["authentication"]["password"], password):
            return jsonify({"status": "error", "message": "Invalid credentials"}), 401

        access_token = create_access_token(identity=user["profile"]["email"])
        refresh_token = create_refresh_token(identity=user["profile"]["email"])

        return jsonify({"status": "success", "access_token": access_token, "refresh_token": refresh_token}), 200

    except Exception as error:
        return jsonify({"status": "error", "message": str(error)}), 500


@auth_bp.route("/auth/token/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)

        return jsonify({"status": "success", "access_token": access_token}), 200

    except Exception as error:
        return jsonify({"status": "error", "message": str(error)}), 500


@auth_bp.route("/auth/token/validate", methods=["POST"])
@jwt_required()
def validate():
    try:
        current_user = get_jwt_identity()
        return jsonify({"status": "success", "message": "Token is valid", "user": current_user}), 200

    except Exception as error:
        return jsonify({"status": "error", "message": str(error)}), 500


@auth_bp.route('/auth/login/google')
def google_login():
    google = current_app.google
    redirect_uri = url_for(
        'parent_bp.auth_bp.google_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@auth_bp.route('/auth/login/google/authorize')
def google_authorize():
    try:
        google = current_app.google
        token = google.authorize_access_token()
        userinfo_endpoint = 'https://www.googleapis.com/oauth2/v1/userinfo'
        resp = google.get(userinfo_endpoint, token=token)
        resp.raise_for_status()  # Raise an exception for HTTP errors

        user_info = resp.json()
        email = user_info['email']

        user = current_app.db.users.find_one({"profile.email": email})
        if not user:
            new_user = {
                "profile": {
                    "username": None,
                    "email": email
                },
                "authentication": {
                    "password": None,
                    "profileCreation": "Google-oauth",
                    "accountStatus": "active",
                    "lastLoginDate": datetime.now()
                }
            }
            current_app.db.users.insert_one(new_user)

        access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email)

    except HTTPError as http_err:
        # Handle HTTP errors from Google API
        return jsonify({"status":"error", 'message': f'Google API error {http_err}'}), 502
    except Exception as error:
        # Handle other errors such as database errors or unexpected issues
        return jsonify({ "status":"error",'message': f'Internal server error {error}'}), 500

    query_string = urlencode({"access_token": access_token, "refresh_token": refresh_token})
    react_app_url = current_app.config['REACT_APP_URL']
    redirect_url = f"{react_app_url}/login-successful?{query_string}"

    return redirect(redirect_url)


@auth_bp.errorhandler(OAuthError)
def handle_oauth_error(error):
    """
    error handler for google auth

    Parameters:
    - error (obj) : error object to be passed into function

    Returns:
    - error message (obj (json)) : error message to be returned to user
    """
    return jsonify({"status": "error", "message": str(error.description)}), 500
