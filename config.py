from dotenv import load_dotenv
import os
from datetime import timedelta

load_dotenv()

class Config:
    # core flask
    PREFERRED_URL_SCHEME = 'https'
    SSL_REDIRECT = True
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))
    
    # database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///.databaseFiles/devlog.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # session 
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Content Security Policy
    CSP = {
        'default-src': "'self'",
        'script-src': "'self'",
        'style-src': "'self' https://fonts.googleapis.com",
        'img-src': "'self' data:",
        'font-src': "'self' https://fonts.gstatic.com",
        'frame-ancestors': "'none'",
        'form-action': "'self'"
    }
    
    # security headers
    SECURE_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }
    
    # email Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    
    # rate Limiting
    RATELIMIT_DEFAULT = "100/hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # file Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_EXTENSIONS = ['.jpg', '.png', '.gif']
    
    # cache Configuration
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 300
