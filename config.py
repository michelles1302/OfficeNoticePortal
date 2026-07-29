import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class Config:
    """Base configuration class containing shared settings."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'replace-with-a-secure-key-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session Security & Timeout Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get( "DATABASE_URL","sqlite:///office_notice.db")

class TestingConfig(Config):
    """Testing configuration with separate database and faster settings."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TESTING_DATABASE_URL',
        "sqlite:///office_notice_test.db"
    )
    BCRYPT_LOG_ROUNDS = 4  # Minimal complexity for fast test execution
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration with strict security measures."""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Enforce secure cookies in production (requires HTTPS)
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True

# Configuration dictionary mapping environment names to classes
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
