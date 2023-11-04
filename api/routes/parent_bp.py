from flask import Blueprint

from .auth.auth_bp import auth_bp
from .claims.claims_bp import claims_bp

parent_bp = Blueprint("parent_bp", __name__)

# register child blueprints
parent_bp.register_blueprint(auth_bp)
parent_bp.register_blueprint(claims_bp)