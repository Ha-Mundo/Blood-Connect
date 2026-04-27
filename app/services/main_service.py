import datetime
from app.models import User, BloodDonation, BloodRequest
from app.extensions import db, bcrypt
from app.services.email_service import EmailService
from time_limit import threshold_request


class MainService:

    @staticmethod
    def get_global_stats(user):
        today = datetime.date.today()
        stats = {
            'donations': 0,
            'requests': 0,
            'total_available': 0
        }
        

        latest_donation = BloodDonation.query.filter_by(
            email=user.email
        ).order_by(BloodDonation.id.desc()).first()

        if latest_donation:
            next_date = latest_donation.next_donation
            if next_date and next_date == today:
                EmailService.send_donation_available_email(user, next_date)


        latest_request = BloodRequest.query.filter_by(
            requester_email=user.email
        ).order_by(BloodRequest.id.desc()).first()

        if latest_request:
            next_date = threshold_request(latest_request.request_date)
            if next_date == today:
                EmailService.send_request_available_email(user, next_date)

        # Protection: DB not ready / missing tables
        try:
            stats['total_available'] = BloodDonation.query.filter_by(
                status='Approved'
            ).count()
        except Exception:
            stats['total_available'] = 0

        if user.is_authenticated:
            try:
                stats['donations'] = BloodDonation.query.filter_by(
                    email=user.email,
                    status='Completed'
                ).count()

                stats['requests'] = BloodRequest.query.filter_by(
                    requester_email=user.email,
                    status='Completed'
                ).count()
            except Exception:
                stats['donations'] = 0
                stats['requests'] = 0

        return stats

    @staticmethod
    def get_admin_stats():
        return {
            'total_users': User.query.count(),
            'total_donations': BloodDonation.query.count(),
            'total_requests': BloodRequest.query.count()
        }

    @staticmethod
    def update_profile(user, form):
        if form.username.data:
            user.username = form.username.data.lower()

        if form.blood_group.data:
            user.blood_group = form.blood_group.data.lower()

        if form.new_password.data:
            user.password = bcrypt.generate_password_hash(
                form.new_password.data
            ).decode('utf-8')

        db.session.commit()

    @staticmethod
    def get_user_activity(user):
        return {
            'completed_donations': BloodDonation.query.filter_by(
                email=user.email,
                status='Completed'
            ).count(),
            'completed_requests': BloodRequest.query.filter_by(
                requester_email=user.email,
                status='Completed'
            ).count()
        }