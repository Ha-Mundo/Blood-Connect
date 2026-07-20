""" Application configuration """

import os
from dotenv import load_dotenv
from sqlalchemy.pool import NullPool

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:

    # =========================
    # CORE
    # =========================
    SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-dev-key")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # =========================
    # DATABASE
    # =========================
    DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

    if DATABASE_URL:
        # Production (Render + Neon)
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace(
                "postgres://",
                "postgresql://",
                1
            )

        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Local development
        SQLALCHEMY_DATABASE_URI = (
            f"sqlite:///{os.path.join(basedir, 'instance', 'blood_connect.db')}"
        )
        
    if DATABASE_URL and DATABASE_URL.startswith("postgres"):
        # SQLALCHEMY ENGINE OPTIONS - IMPORTANT FOR NEON + RENDER
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True,
            "pool_recycle": 300,
            "poolclass": NullPool,
            "connect_args": {
                "sslmode": "require"
            }
        }
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {}
    
    # =========================
    # MAIL
    # =========================
    MAIL_SERVER = os.getenv("MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))

    # case-insensitive sure conversion for Render
    MAIL_USE_TLS = str(os.getenv("MAIL_USE_TLS", "True")).lower() in ["true", "1", "yes"]
    MAIL_USE_SSL = str(os.getenv("MAIL_USE_SSL", "False")).lower() in ["true", "1", "yes"]

    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    MAIL_DEFAULT_SENDER = (
        os.getenv("MAIL_DEFAULT_SENDER_NAME", "Blood Connect"),
        os.getenv("MAIL_DEFAULT_SENDER_EMAIL", "no-reply@example.com")
    )

    # =========================
    # SECURITY
    # =========================
    PREFERRED_URL_SCHEME = "https"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"

    # Enable only in production HTTPS
    SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"
    REMEMBER_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"
    
