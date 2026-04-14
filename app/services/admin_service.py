import csv
from datetime import date, timedelta
from io import StringIO
from flask import abort
from app.extensions import db
from app.models import User, BloodDonation, BloodRequest


class AdminService:
    @staticmethod
    def get_users_page(page, search=None, status=None, verified=None, per_page=10):
        query = User.query

        if search:
            search = search.strip()
            query = query.filter(
                (User.username.contains(search)) | (User.email.contains(search))
            )

        if status in {"active", "banned"}:
            query = query.filter_by(is_active=(status == "active"))

        if verified in {"1", "0"}:
            query = query.filter_by(is_verified=(verified == "1"))

        pagination = query.order_by(User.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return pagination, query.count()

    @staticmethod
    def get_requests_page(page, search=None, blood_group=None, status=None, per_page=10):
        query = BloodRequest.query

        if search:
            search_term = search.strip().lower()
            query = query.filter(
                (BloodRequest.name.contains(search_term)) |
                (BloodRequest.requester_email.contains(search_term)) |
                (BloodRequest.city.contains(search_term))
            )

        if blood_group:
            query = query.filter_by(blood_groups=blood_group.lower())

        if status:
            query = query.filter_by(status=status)

        pagination = query.order_by(BloodRequest.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        count = query.count()

        donor_names = {}
        emails_to_fetch = [req.donor_email for req in pagination.items if req.donor_email]

        if emails_to_fetch:
            donors = BloodDonation.query.filter(BloodDonation.email.in_(emails_to_fetch)).all()
            donor_names = {d.email: d.name for d in donors}

        return pagination, count, donor_names

    from flask import abort

    @staticmethod
    def toggle_user(user_id):
        user = db.session.get(User, user_id)

        if not user:
            abort(404)

        if user.role == "admin":
            return user, "You cannot ban another administrator!"

        user.is_active = not user.is_active

        if not user.is_active:
            BloodDonation.query.filter_by(
                email=user.email, status="Pending"
            ).update({"status": "Cancelled"})

            pending_requests = BloodRequest.query.filter_by(
                requester_email=user.email,
                status="Pending"
            ).all()

            for req in pending_requests:
                donation = BloodDonation.query.filter_by(
                    email=req.donor_email,
                    blood_groups=req.blood_groups,
                    status="Claimed"
                ).first()

                if donation:
                    donation.status = "Pending"

                req.status = "Cancelled"

        db.session.commit()

        status_text = (
            "banned and their active records cleared"
            if not user.is_active
            else "activated"
        )

        return user, status_text

    @staticmethod
    def build_csv(table_type):
        si = StringIO()
        cw = csv.writer(si)

        if table_type == "donations":
            records = BloodDonation.query.all()
            cw.writerow(['ID', 'Name', 'Email', 'Age', 'Blood Group', 'City', 'Status', 'Latest Donation', 'Next Donation'])
            for r in records:
                cw.writerow([r.id, r.name, r.email, r.age, r.blood_groups, r.city, r.status, r.latest_donation, r.next_donation])

        elif table_type == "requests":
            records = BloodRequest.query.all()
            cw.writerow(['ID', 'Recipient Name', 'Requester Email', 'Blood Group', 'City', 'Status', 'Request Date'])
            for r in records:
                cw.writerow([r.id, r.name, r.requester_email, r.blood_groups, r.city, r.status, r.request_date])

        else:
            raise ValueError("Invalid table type")

        return si.getvalue()

    @staticmethod
    def cleanup_records():
        threshold_date = date.today() - timedelta(days=30)

        deleted_donations = BloodDonation.query.filter(
            BloodDonation.status.in_(["Cancelled", "Unsuccessful"]),
            BloodDonation.latest_donation < threshold_date
        ).delete(synchronize_session=False)

        deleted_requests = BloodRequest.query.filter(
            BloodRequest.status.in_(["Cancelled", "Unsuccessful"]),
            BloodRequest.request_date < threshold_date
        ).delete(synchronize_session=False)

        db.session.commit()
        return deleted_donations, deleted_requests