""" Application factory and initialization """
from flask import Flask
from config import Config
from app.extensions import db, bcrypt, csrf, login_manager, mail, limiter
from app.extensions import talisman
from app.models import User

def create_app(config_class=Config):
    """ Initialize flask talisman """
    if app.config.get("FLASK_ENV") == "production":
        talisman.init_app(
            app,
            force_https=True,
            session_cookie_secure=True,
            content_security_policy=None
        )
        
    """ Initialize the core application """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with the app context
    db.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints 
    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp
    from app.blood_operations.routes import blood_ops_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(blood_ops_bp)

    return app