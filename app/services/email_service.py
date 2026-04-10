from flask_mail import Message
from flask import url_for

from app.extensions import mail


class EmailService:

    @staticmethod
    def send_confirmation_email(user, token):
        confirm_url = url_for('auth.confirm_email', token=token, _external=True)

        msg = Message(
            "Confirm your account",
            recipients=[user.email]
        )

        msg.html = f"<p>Click here: <a href='{confirm_url}'>Confirm Email</a></p>"
        mail.send(msg)

    @staticmethod
    def send_reset_email(user, token):
        reset_url = url_for('auth.reset_token', token=token, _external=True)

        msg = Message(
            "Password Reset Request",
            recipients=[user.email]
        )

        msg.body = f"Reset here: {reset_url}"
        mail.send(msg)