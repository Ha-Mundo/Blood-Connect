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
            "Confirm Your Email Address - Blood Donation Portal",
            recipients=[user.email]
        )

        msg.body = f"""
            Hello {user.username},
            Thank you for registering with the Blood Donation Portal.
            To activate your account and verify your email address, please visit the following link:
            {confirm_url}
            If you did not create an account, you can safely ignore this email.
            Kind regards,
            Blood Donation Portal Team
            """
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
            "Password Reset Request - Blood Donation Portal",
            recipients=[user.email]
        )

        msg.body = f"""
            Hello {user.username},
            We received a request to reset the password for your Blood Donation Portal account.
            To choose a new password, please visit the link below:
            {reset_url}
            If you did not request a password reset, no further action is required and your account remains secure.
            For security reasons, this link may expire after a limited period of time.
            Kind regards,
            Blood Donation Portal Team
            """
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
            body = f"""
                Hello {user.username},
                We are pleased to inform you that you are now eligible to donate blood again.
                Your continued support plays a vital role in helping patients in need, and we sincerely appreciate your contribution to the community.
                Thank you for being a blood donor.
                Best regards,
                The Blood Donation Team
                """

        elif type_ == "request":
            subject = "You Can Submit a New Blood Request"
            body = f"""
                Hello {user.username},
                We would like to inform you that you are now eligible to submit a new blood request if needed.
                Should you require assistance, you may access the platform and create a new request at any time.
                Best regards,
                The Blood Donation Team
                """

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

        body = f"""
            Hello {donation.name.title()},
            We are pleased to inform you that your blood donation request (Reference #{donation.id}) has been matched with a patient in need.
            Please visit the nearest designated hospital or donation center in {donation.city.title()} to complete the donation process. Medical staff will guide you through the next steps.
            Your willingness to donate can make a meaningful difference in someone's life.
            Thank you for your generosity and support.
            Best regards,
            The Blood Donation Team
            """

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
            body = f"""
                Hello {donation.name.title()},
                We are pleased to inform you that your blood donation (Reference #{donation.id}) has been reviewed and approved.
                A member of the medical team may contact you if additional information or coordination is required.
                Thank you for your willingness to help others through blood donation. Your contribution is greatly appreciated.
                Best regards,
                The Blood Donation Team
                """

        elif status == "Unsuccessful":
            subject = f"Update on your Blood Donation #{donation.id}"
            body = f"""
                Hello {donation.name.title()},
                We regret to inform you that your blood donation (Reference #{donation.id}) has been marked as unsuccessful.
                There may be several reasons for this outcome. If you would like further information, please contact the relevant donation center or healthcare facility.
                We sincerely appreciate your willingness to donate and thank you for your support.
                Best regards,
                The Blood Donation Team
                """

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
            body = f"""
                Hello {request.name.title()},
                We are pleased to inform you that your blood request (Reference #{request.id}) has been reviewed and approved.
                What happens next?
                A member of our clinical team will contact you shortly to coordinate the next steps and ensure the process moves forward as smoothly as possible.
                If you have any questions in the meantime, please do not hesitate to contact us.
                Best regards,
                The Blood Donation Team
                """
        elif status == "Unsuccessful":
            subject = f"Update on your Blood Request #{request.id} "
            body = f"""
                Hello {request.name.title()},
                We regret to inform you that your blood request (Reference #{request.id}) has not been approved.
                This decision may be related to eligibility requirements, missing information, or other administrative or medical considerations.
                If you believe additional information may be relevant, please contact the support team for further assistance.
                Best regards,
                The Blood Donation Team
                """

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
            "Account Update - Blood Donation Portal",
            recipients=[user.email],
        )

        msg.body = f"""
            Hello {user.username},
            We would like to inform you that the status of your account has been updated.
            {message}
            If you have any questions regarding this update, please contact the support team.
            Best regards,
            The Blood Donation Team
            """

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
            body = f"""
                Hello {name.title()},
                Thank you for completing your blood donation.
                Your generosity and commitment can help save lives and provide critical support to patients in need.
                We sincerely appreciate your contribution and thank you for being part of our donor community.
                Best regards,
                The Blood Donation Team
                """

        elif type_ == "request":
            subject = "Your request has been fulfilled"
            body = f"""
                Hello {name.title()},
                We are pleased to inform you that your blood request has been successfully fulfilled.
                We hope the support provided contributes positively to your treatment and recovery.
                Thank you for using our platform, and we wish you all the best.
                Best regards,
                The Blood Donation Team
                """

        msg = Message(subject, recipients=[user.email])
        msg.body = body
        try:
            mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f"Email error: {e}")          
            return False
