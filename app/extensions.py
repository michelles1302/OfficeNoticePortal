from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# Instantiate the extensions. By declaring them here, we prevent circular
# dependencies when importing extensions in other parts of the application.
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()

# Basic Flask-Login configurations (to be utilized in Module 3)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'danger'
login_manager.login_message = 'Please log in to access this page.'
