from flask import Blueprint

notice_bp = Blueprint('notice', __name__)

# Register notice blueprint routes
from app.blueprints.notice import routes
