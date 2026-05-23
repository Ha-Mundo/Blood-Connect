""" Centralized Flask extensions initialization """
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman


db = SQLAlchemy()
bcrypt = Bcrypt()
csrf = CSRFProtect()
talisman = Talisman()
mail = Mail()

login_manager = LoginManager()
login_manager.login_view = 'auth.login' # Note the blueprint prefix 'auth.'
login_manager.login_message_category = 'info'

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["500 per day", "100 per hour"],
    storage_uri="memory://"
)