""" Application configuration class """
import os
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-very-unsafe')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'instance', 'BloodDonationSystem.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail settings (Mailpit)
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_DEFAULT_SENDER = ('Blood Donation System', 'test@mail.com')