from flask import Blueprint

employee_bp = Blueprint('employee', __name__)

# Register employee blueprint routes
from app.blueprints.employee import routes
