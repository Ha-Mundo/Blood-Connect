from flask_mail import Message
from flask import url_for, current_app

from app.extensions import mail

class EmailService:
    
    @staticmethod
    def _can_send(user):
        return user and user.email_notifications

    @staticmethod
    def send_confirmation_email(user, token):
        confirm_url = url_for('auth.confirm_email', token=token, _external=True)

        msg = Message(
            "Confirm your account",
            recipients=[user.email]
        )

        msg.html = f"<p>Click here: <a href='{confirm_url}'>Confirm Email</a></p>"
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"Email error: {e}")

    @staticmethod
    def send_reset_email(user, token):
        reset_url = url_for('auth.reset_token', token=token, _external=True)

        msg = Message(
            "Password Reset Request",
            recipients=[user.email]
        )

        msg.body = f"Reset here: {reset_url}"
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"Email error: {e}")
        
    @staticmethod
    def send_eligibility_notification(user, type_):
        if not EmailService._can_send(user):
            return
        
        subject = ""
        body = ""

        if type_ == "donation":
            subject = "You can donate blood again"
            body = "You are now eligible to donate blood again. Thank you for your contribution!"

        elif type_ == "request":
            subject = "You can request blood again"
            body = "You can now make a new blood request if needed."

        msg = Message(subject, recipients=[user.email])
        msg.body = body
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"Email error: {e}")
        
    @staticmethod
    def send_donation_claimed_notification(user, donation):
        if not EmailService._can_send(user):
            return
        
        subject = f"Your blood donation #{donation.id} has been requested"

        body = (
            f"Hello {donation.name.title()},\n\n"
            f"Good news! A patient has requested your blood donation #{donation.id}.\n\n"
            f"Please proceed to the nearest hospital in {donation.city.title()} "
            f"to complete the donation process.\n\n"
            f"Thank you for saving lives!"
        )

        msg = Message(subject, recipients=[donation.email])
        msg.body = body
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"Email error: {e}")
        
    @staticmethod
    def send_donation_status_notification(user, donation, status):
        if not EmailService._can_send(user):
            return
        
        subject = ""
        body = ""

        if status == "Approved":
            subject = f"Blood Donation #{donation.id} Approved "
            body = (
                f"Hello {donation.name.title()},\n\n"
                f"Great news! Your blood donation #{donation.id} has been approved and you'll be contacted soon. "
                f"Thank you for your contribution."
            )

        elif status == "Unsuccessful":
            subject = f"Update on your Blood Donation #{donation.id}"
            body = (
                f"Hello {donation.name.title()},\n\n"
                f"Your donation #{donation.id} has been marked as unsuccessful.\n"
                f"Please contact the center for more info."
            )

        if subject:
            msg = Message(subject, recipients=[donation.email])
            msg.body = body
            try:
                mail.send(msg)
            except Exception as e:
                current_app.logger.error(f"Email error: {e}")


    @staticmethod
    def send_request_status_notification(user, request, status):
        if not EmailService._can_send(user):
            return
        
        subject = ""
        body = ""

        if status == "Approved":
            subject = f"Blood Request #{request.id} Approved"
            body = (
                f"Hello {request.name.title()},\n\n"
                f"We are pleased to inform you that your blood request #{request.id} has been reviewed and approved.\n\n"
                f"What happens next? A member of our clinical team will contact you shortly to coordinate "
                f"the next steps and ensure everything moves forward smoothly.\n\n"
                f"In the meantime, if you have any questions, feel free to reply to this email.\n\n"
                f"Best regards,\n"
                f"The Blood Donation Team"
            )

        elif status == "Unsuccessful":
            subject = f"Update on your Blood Request #{request.id} "
            body = (
                f"Hello {request.name.title()},\n\n"
                f"Your request #{request.id} has been marked as unsuccessful."
            )

        if subject:
            msg = Message(subject, recipients=[request.requester_email])
            msg.body = body
            try:
                mail.send(msg)
            except Exception as e:
                current_app.logger.error(f"Email error: {e}")


    @staticmethod
    def send_user_status_notification(user, message):
        if not EmailService._can_send(user):
            return
        
        msg = Message(
            "Account Update - Blood Donation Portal",
            recipients=[user.email],
        )

        msg.body = (
            f"Hello {user.username},\n\n"
            f"Your account status has been updated.\n\n"
            f"{message}"
        )

        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"Email error: {e}")
        
    
    @staticmethod
    def send_thank_you_email(user, name, type_):
        if not EmailService._can_send(user):
            return


        if type_ == "donation":
            subject = "Thank you for your donation ❤️"
            body = (
                f"Hello {name.title()},\n\n"
                f"Thank you for completing your blood donation.\n"
                f"Your contribution can save lives."
            )

        elif type_ == "request":
            subject = "Your request has been fulfilled"
            body = (
                f"Hello {name.title()},\n\n"
                f"Your blood request has been successfully completed.\n"
                f"We wish you the best."
            )

        msg = Message(subject, recipients=[user.email])
        msg.body = body
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"Email error: {e}")