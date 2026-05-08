import os
from dotenv import load_dotenv

load_dotenv()


# Absolute path to the backend/ directory so uploads always resolve correctly
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
def _split_csv(value):
    if not value:
        return []
    return [item.strip() for item in value.split(',') if item.strip()]

# Absolute path to the backend/ directory 
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def get_database_url():
    url = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(BASE_DIR, 'driftdater.db'))
    # Render provides postgres:// but SQLAlchemy needs postgresql://
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    return url

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') #, 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(BASE_DIR, 'driftdater.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Absolute path — works on Windows and Linux regardless of working directory
    UPLOAD_FOLDER = os.path.join(BASE_DIR, os.environ.get('UPLOAD_FOLDER', 'uploads'))
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False  # Set True in production with HTTPS
    # Absolute path 
    UPLOAD_FOLDER = os.path.join(BASE_DIR, os.environ.get('UPLOAD_FOLDER', 'uploads'))
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    SESSION_COOKIE_NAME = 'driftdater_session'
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True  
    
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_DOMAIN = os.environ.get('SESSION_COOKIE_DOMAIN') or None
    REMEMBER_COOKIE_NAME = 'driftdater_remember'
    REMEMBER_COOKIE_SAMESITE = 'None'
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    CORS_ORIGINS = _split_csv(os.environ.get('CORS_ORIGINS')) or [
        "http://localhost:5173", 
        "http://127.0.1:5173", 
        "https://driftdater-frontend-7s49.onrender.com"
    ]
