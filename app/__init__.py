import os
from flask import Flask
from config import config
from app.extensions import db, migrate, bcrypt, login_manager

def create_app(config_name=None):
    """
    Application factory function. Creates, configures, and returns 
    the Flask application instance.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
        
    app = Flask(__name__)
    
    # Load configuration settings
    app.config.from_object(config.get(config_name, config['default']))
    
    # Initialize extensions with the application instance
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints (routing modules)
    from app.blueprints.auth import auth_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.employee import employee_bp
    from app.blueprints.notice import notice_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(employee_bp, url_prefix='/')
    app.register_blueprint(notice_bp, url_prefix='/notices')
    
    # Register a user_loader callback for Flask-Login (to be fully defined in Module 3)
    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
        
    # Inject Role constants globally into templates
    @app.context_processor
    def inject_role_constants():
        from app.models.role import Role
        return dict(Role=Role)

    return app
