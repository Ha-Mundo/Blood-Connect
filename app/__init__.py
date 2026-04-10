""" Application factory and initialization """
from flask import Flask
from config import Config
from app.extensions import db, bcrypt, csrf, login_manager, mail, limiter
from app.models import User

def create_app(config_class=Config):
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
    from app.main.routes import main
    from app.auth.routes import auth
    from app.admin.routes import admin
    from app.blood_operations.routes import blood_ops
    
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(blood_ops)

    return app