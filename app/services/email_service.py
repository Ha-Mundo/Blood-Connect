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
            "Confirm Your Email Address - Blood Connect",
            recipients=[user.email]
        )

        msg.body = (
            f"Hello {user.username},\n\n"
            "Thank you for registering with the Blood Connect.\n"
            "To activate your account and verify your email address, please visit the following link:\n"
            f"{confirm_url}\n"
            "If you did not create an account, you can safely ignore this email.\n\n"
            "Kind regards,\n\n"
            "The Blood Connect Team"
        )
        try:
            mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f"Email error: {e}")
            return False

    @staticmethod
    def send_reset_email(user, token):
        reset_url = url_for('auth.reset_token', token=token, _external=True)

        msg = Message(
            "Password Reset Request - Blood Connect",
            recipients=[user.email]
        )

        msg.body = (
            f"Hello {user.username},\n\n"
            "We received a request to reset the password for your Blood Connect account.\n"
            "To choose a new password, please visit the link below:\n"
            f"{reset_url}\n"
            "If you did not request a password reset, no further action is required and your account remains secure.\n"
            "For security reasons, this link may expire after a limited period of time.\n\n"
            "Kind regards,\n\n"
            "The Blood Connect Team"
        )
        try:
            mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f"Email error: {e}")
            return False

    @staticmethod
    def send_eligibility_notification(user, type_):
        if not EmailService._can_send(user):
            return
        
        subject = ""
        body = ""

        if type_ == "donation":
            subject = "You can donate blood again"
            body = (
                f"Hello {user.username},\n\n"
                "We are pleased to inform you that you are now eligible to donate blood again.\n"
                "Your continued support plays a vital role in helping patients in need, and we sincerely appreciate your contribution to the community.\n"
                "Thank you for being a blood donor.\n\n"
                "Best regards,\n\n"
                "The Blood Connect Team"
            )
        elif type_ == "request":
            subject = "You Can Submit a New Blood Request"
            body = (
                f"Hello {user.username},\n\n"
                "We would like to inform you that you are now eligible to submit a new blood request if needed.\n"
                "Should you require assistance, you may access the platform and create a new request at any time.\n\n"
                "Best regards,\n\n"
                "The Blood Connect Team"
            )

        msg = Message(subject, recipients=[user.email])
        msg.body = body
        try:
            mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f"Email error: {e}")
            return False

    @staticmethod
    def send_donation_claimed_notification(user, donation):
        if not EmailService._can_send(user):
            return
        
        subject = f"Your blood donation #{donation.id} has been requested"

        body = (
            f"Hello {donation.name.title()},\n\n"
            f"We are pleased to inform you that your blood donation request (Reference #{donation.id}) has been matched with a patient in need.\n"
            f"Please visit the nearest designated hospital or donation center in {donation.city.title()} to complete the donation process. Medical staff will guide you through the next steps.\n"
            "Your willingness to donate can make a meaningful difference in someone's life.\n"
            "Thank you for your generosity and support.\n\n"
            "Best regards,\n\n"
            "The Blood Connect Team"
        )

        msg = Message(subject, recipients=[donation.email])
        msg.body = body
        try:
            mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f"Email error: {e}")
            return False

    @staticmethod
    def send_donation_status_notification(user, donation, status):
        if not EmailService._can_send(user):
            return
        
        subject = ""
        body = ""

        if status == "Approved":
            subject = f"Blood Donation #{donation.id} Approved"
            body = (
                f"Hello {donation.name.title()},\n\n"
                f"We are pleased to inform you that your blood donation (Reference #{donation.id}) has been reviewed and approved.\n"
                "A member of the medical team may contact you if additional information or coordination is required.\n"
                "Thank you for your willingness to help others through blood donation. Your contribution is greatly appreciated.\n\n"
                "Best regards,\n\n"
                "The Blood Connect Team"
            )
        elif status == "Unsuccessful":
            subject = f"Update on your Blood Donation #{donation.id}"
            body = (
                f"Hello {donation.name.title()},\n\n"
                f"We regret to inform you that your blood donation (Reference #{donation.id}) has been marked as unsuccessful.\n"
                "There may be several reasons for this outcome. If you would like further information, please contact the relevant donation center or healthcare facility.\n"
                "We sincerely appreciate your willingness to donate and thank you for your support.\n\n"
                "Best regards,\n\n"
                "The Blood Connect Team"
            )

        if subject:
            msg = Message(subject, recipients=[donation.email])
            msg.body = body
            try:
                mail.send(msg)
                return True
            except Exception as e:
                current_app.logger.error(f"Email error: {e}")
                return False

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
                f"We are pleased to inform you that your blood request (Reference #{request.id}) has been reviewed and approved.\n"
                "What happens next?\n"
                "A member of our clinical team will contact you shortly to coordinate the next steps and ensure the process moves forward as smoothly as possible.\n"
                "If you have any questions in the meantime, please do not hesitate to contact us.\n\n"
                "Best regards,\n\n"
                "The Blood Connect Team"
            )
        elif status == "Unsuccessful":
            subject = f"Update on your Blood Request #{request.id} "
            body = (
                f"Hello {request.name.title()},\n\n"
                f"We regret to inform you that your blood request (Reference #{request.id}) has not been approved.\n"
                "This decision may be related to eligibility requirements, missing information, or other administrative or medical considerations.\n"
                "If you believe additional information may be relevant, please contact the support team for further assistance.\n\n"
                "Best regards,\n\n"
                "The Blood Connect Team"
            )

        if subject:
            msg = Message(subject, recipients=[request.requester_email])
            msg.body = body
            try:
                mail.send(msg)
                return True
            except Exception as e:
                current_app.logger.error(f"Email error: {e}")
                return False


    @staticmethod
    def send_user_status_notification(user, message):
        if not EmailService._can_send(user):
            return
        
        msg = Message(
            "Account Update - Blood Connect",
            recipients=[user.email],
        )

        msg.body = (
            f"Hello {user.username},\n\n"
            "We would like to inform you that the status of your account has been updated.\n"
            f"{message}\n"
            "If you have any questions regarding this update, please contact the support team.\n\n"
            "Best regards,\n\n"
            "The Blood Connect Team"
        )

        try:
            mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f"Email error: {e}")
            return False
    
    @staticmethod
    def send_thank_you_email(user, name, type_):
        if not EmailService._can_send(user):
            return


        if type_ == "donation":
            subject = "Thank you for your donation ❤️"
            body = (
                f"Hello {name.title()},\n\n"
                "Thank you for completing your blood donation.\n"
                "Your generosity and commitment can help save lives and provide critical support to patients in need.\n"
                "We sincerely appreciate your contribution and thank you for being part of our donor community.\n\n"
                "Best regards,\n\n"
                "The Blood Connect Team"
            )

        elif type_ == "request":
            subject = "Your request has been fulfilled"
            body = (
                f"Hello {name.title()},\n\n"
                "We are pleased to inform you that your blood request has been successfully fulfilled.\n"
                "We hope the support provided contributes positively to your treatment and recovery.\n"
                "Thank you for using our platform, and we wish you all the best.\n\n"
                "Best regards,\n\n"
                "The Blood Connect Team"
            )

        msg = Message(subject, recipients=[user.email])
        msg.body = body
        try:
            mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f"Email error: {e}")          
            return False
