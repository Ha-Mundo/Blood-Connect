""" Application configuration """

import os
from dotenv import load_dotenv

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
    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL:
        # Production (Render + Neon)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace(
            "postgres://",
            "postgresql://",
            1
        )
    else:
        # Local development
        SQLALCHEMY_DATABASE_URI = (
            f"sqlite:///{os.path.join(basedir, 'instance', 'BloodDonationPortal.db')}"
        )

    # =========================
    # MAIL
    # =========================
    MAIL_SERVER = os.getenv("MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 1025))

    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "False") == "True"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False") == "True"

    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    MAIL_DEFAULT_SENDER = (
        os.getenv("MAIL_SENDER_NAME", "Blood Donation Portal"),
        os.getenv("MAIL_DEFAULT_SENDER", "BDP@mail.com")
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

