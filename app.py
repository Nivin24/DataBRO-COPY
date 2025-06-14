from flask import Flask
from extensions import db
from dotenv import load_dotenv
from flask_session import Session
import os

# Allow OAuth over HTTP (for local testing only)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Load environment variables from .env file
load_dotenv()

# ========================
# Application Factory
# ========================
def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Basic Configuration
    app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = './flask_session'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False  # 🔐 Set to True in production
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize Extensions
    Session(app)
    db.init_app(app)

    # Register Blueprints
    from routes.api import api_bp
    from routes.badge_routes import badge_bp
    from routes.dashboard import dashboard_bp
    from routes.editor import editor_bp
    from routes.error_handlers import error_handlers_bp
    from routes.home_routes import home_bp
    from routes.login_routes import login_bp
    from routes.profile import profile_bp
    from routes.settings import settings_bp
    from routes.topic_routes import topic_bp
    from routes.user_activity import user_activity_bp
    from routes.contact_routes import contact_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(badge_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(editor_bp)
    app.register_blueprint(error_handlers_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(topic_bp)
    app.register_blueprint(user_activity_bp)
    app.register_blueprint(contact_bp)

    return app


# ========================
# Run the App
# ========================
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)