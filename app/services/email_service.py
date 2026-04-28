from flask_mail import Message
from flask import url_for, current_app

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
        
    @staticmethod
    def send_eligibility_notification(email, type_):
        subject = ""
        body = ""

        if type_ == "donation":
            subject = "You can donate blood again"
            body = "You are now eligible to donate blood again. Thank you for your contribution!"

        elif type_ == "request":
            subject = "You can request blood again"
            body = "You can now make a new blood request if needed."

        msg = Message(subject, recipients=[email])
        msg.body = body
        mail.send(msg)
        
    @staticmethod
    def send_donation_claimed_notification(donation):
        subject = "Your blood donation has been requested"

        body = (
            f"Hello {donation.name.capitalize()},\n\n"
            f"Good news! A patient has requested your blood donation.\n\n"
            f"Please proceed to the nearest hospital in {donation.city.capitalize()} "
            f"to complete the donation process.\n\n"
            f"Thank you for saving lives!"
        )

        msg = Message(subject, recipients=[donation.email])
        msg.body = body
        mail.send(msg)