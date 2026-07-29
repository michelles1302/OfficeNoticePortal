from flask import Blueprint

# Instantiate blueprint module
auth_bp = Blueprint('auth', __name__)

# Import routes to register them with the blueprint object
from app.blueprints.auth import routes
