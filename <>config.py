"""
Configuration settings for the application
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', False)
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configurations
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost:5432/data_cleaning'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # MongoDB configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/data_cleaning')
    
    # Upload configuration
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size
    ALLOWED_EXTENSIONS = {'csv', 'json', 'xlsx', 'xls', 'xml', 'parquet', 'tsv'}
    
    # Cleaning configuration
    DUPLICATE_CHECK = True
    MISSING_VALUE_HANDLING = True
    OUTLIER_DETECTION = True

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
