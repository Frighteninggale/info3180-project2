from flask import Flask
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_login import LoginManager

from app.routes import main_bp
import os

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app(config_class=None):
    app = Flask(__name__)

    if config_class is None:
        from config import Config
        app.config.from_object(Config)
    else:
        app.config.from_object(config_class)

    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = 'dev-secret-key'  # Fallback for development if not set in env

    # Ensure upload folder exists
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

     # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)


# CORS — allow local dev and any Render frontend subdomain
    allowed_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://*.onrender.com"
    ]
    # If a specific frontend URL is set via env var, add it too
    frontend_url = os.environ.get('FRONTEND_URL')
    if frontend_url:
        allowed_origins.append(frontend_url)

    CORS(app, 
     origins=["http://localhost:5173", "http://127.0.0.1:5173","https://driftdater-frontend-7s49.onrender.com"],
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])


    # Import models so Flask-Migrate picks them up
    from app.models import user, profile, match, message, favourite

    # Register blueprints
   
    # with app.app_context():
    #     db.create_all()
    #     print(" Database tables created/verified!")


    # Register blueprint
    from app.routes import main_bp 
    from app.routes.auth import auth_bp
    from app.routes.profiles import profiles_bp
    from app.routes.matches import matches_bp
    from app.routes.messages import messages_bp
    from app.routes.search import search_bp
    from app.routes.favourites import favourites_bp



    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(profiles_bp, url_prefix='/api/profiles')
    app.register_blueprint(matches_bp, url_prefix='/api/matches')
    app.register_blueprint(messages_bp, url_prefix='/api/messages')
    app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(favourites_bp, url_prefix='/api/favourites')


    

    return app

# Create the app instance for gunicorn
app = create_app()

# Run database migrations on startup
with app.app_context():
    upgrade()