from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    # security config
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24)) #random session key
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///.databaseFiles/devlog.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CSP = {
        # injection protection csp
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline'",
        'style-src': "'self' 'unsafe-inline'",
        'img-src': "'self' data:",
        'font-src': "'self'",
    }
