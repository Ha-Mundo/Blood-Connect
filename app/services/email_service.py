from flask_mail import Message
from flask import url_for, current_app

from app.extensions import mail
from app.models import User


class EmailService:
    
    _user_cache = {}

    @staticmethod
    def _can_send(user=None, email=None):
        if user:
            return user.email_notifications

        if email:
            if email in EmailService._user_cache:
                return EmailService._user_cache[email]

            user = User.query.filter_by(email=email).first()
            result = user and user.email_notifications
            EmailService._user_cache[email] = result
            return result

        return False

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
        if not EmailService._can_send(email=email):
            return
        
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
        if not EmailService._can_send(email=donation.email):
            return
        
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
        
    @staticmethod
    def send_donation_status_notification(donation, status):
        if not EmailService._can_send(email=donation.email):
            return
        
        subject = ""
        body = ""

        if status == "Approved":
            subject = "Blood Donation Approved"
            body = (
                f"Hello {donation.name.capitalize()},\n\n"
                f"Great news! Your blood donation has been approved. "
                f"Thank you for your contribution."
            )

        elif status == "Unsuccessful":
            subject = "Update on your Blood Donation"
            body = (
                f"Hello {donation.name.capitalize()},\n\n"
                f"Your donation has been marked as unsuccessful.\n"
                f"Please contact the center for more info."
            )

        if subject:
            msg = Message(subject, recipients=[donation.email])
            msg.body = body
            mail.send(msg)


    @staticmethod
    def send_request_status_notification(request, status):
        if not EmailService._can_send(email=request.requester_email):
            return
        
        subject = ""
        body = ""

        if status == "Approved":
            subject = "Blood Request Approved"
            body = (
                f"Hello {request.name.capitalize()},\n\n"
                f"Your blood request has been approved."
            )

        elif status == "Unsuccessful":
            subject = "Update on your Blood Request"
            body = (
                f"Hello {request.name.capitalize()},\n\n"
                f"Your request has been marked as unsuccessful."
            )

        if subject:
            msg = Message(subject, recipients=[request.requester_email])
            msg.body = body
            mail.send(msg)


    @staticmethod
    def send_user_status_notification(user, message):
        if not EmailService._can_send(user=user):
            return
        
        msg = Message(
            "Account Update - Blood Donation System",
            recipients=[user.email],
        )

        msg.body = (
            f"Hello {user.username},\n\n"
            f"Your account status has been updated.\n\n"
            f"{message}"
        )

        mail.send(msg)
        
    
    @staticmethod
    def send_thank_you_email(user=None, email=None, name="", type_=""):
        if not EmailService._can_send(user=user, email=email):
            return


        if type_ == "donation":
            subject = "Thank you for your donation ❤️"
            body = (
                f"Hello {name.capitalize()},\n\n"
                f"Thank you for completing your blood donation.\n"
                f"Your contribution can save lives."
            )

        elif type_ == "request":
            subject = "Your request has been fulfilled"
            body = (
                f"Hello {name.capitalize()},\n\n"
                f"Your blood request has been successfully completed.\n"
                f"We wish you the best."
            )

        msg = Message(subject, recipients=[email])
        msg.body = body
        mail.send(msg)