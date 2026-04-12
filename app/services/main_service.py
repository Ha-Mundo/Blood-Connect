from app.models import User, BloodDonation, BloodRequest
from app.extensions import db, bcrypt


class MainService:

    @staticmethod
    def get_global_stats(user):
        stats = {
            'donations': 0,
            'requests': 0,
            'total_available': BloodDonation.query.filter_by(status='Approved').count()
        }

        if user.is_authenticated:
            stats['donations'] = BloodDonation.query.filter_by(
                email=user.email,
                status='Completed'
            ).count()

            stats['requests'] = BloodRequest.query.filter_by(
                requester_email=user.email,
                status='Completed'
            ).count()

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