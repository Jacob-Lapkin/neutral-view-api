# pylint: disable=broad-exception-caught
from flask import Blueprint, jsonify, request, current_app, url_for
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuthError

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
        password_match = data.get("passwordMath", None)

        # check if all required data is provided
        if not all ([email, password, password_match]):
            return jsonify({"status":"error","message":"Required registration information missing"}), 400
        
        # check if passwords match:
        if password != password_match:
            return jsonify({"status":"error", "message":"passwords do not match"}), 400
        

        # check if user exists in database
        user = db.users.find_one({
            "$or": [
                {"email": email}
            ]
        })

        if user:
            return({"status":"error", "message":"Email has already been registered"}), 400
        
        # create password hash
        hashed_password = generate_password_hash(password=password)

        # insert user into database
        new_user = db.users.insert_one({"email":email,"password":hashed_password})

        return jsonify({"status":"success", "messaage":f"successfully registered new user {new_user.id}"}), 201
        
        
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
        
        user = db.users.find_one({"email": email})

        if not user or not check_password_hash(user["password"], password):
            return jsonify({"status": "error", "message": "Invalid credentials"}), 401

        access_token = create_access_token(identity=user["email"])
        refresh_token = create_refresh_token(identity=user["email"])

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
    redirect_uri = url_for('google_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@auth_bp.route('/auth/login/google/authorize')
def google_authorize():
    google = current_app.google
    token = google.authorize_access_token()
    resp = google.get('userinfo', token=token)
    user_info = resp.json()

    # You can now create a JWT token using this user_info or store it in your database.
    # This is just an example, in a real-world scenario you would handle the user data 
    # more thoroughly by checking if the user already exists, etc.

    email = user_info['email']

    # Check if user exists in your db
    user = current_app.db.users.find_one({"email": email})

    if not user:
        # Insert the new user into your database or handle as you wish
        current_app.db.users.insert_one({"email": email})

    # Create JWT tokens as in your login route
    access_token = create_access_token(identity=email)
    refresh_token = create_refresh_token(identity=email)

    return jsonify({"status": "success", "access_token": access_token, "refresh_token": refresh_token}), 200


@auth_bp.errorhandler(OAuthError)
def handle_oauth_error(e):
    return jsonify({"status": "error", "message": str(e.description)}), 500