from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

# Register admin blueprint routes
from app.blueprints.admin import routes
