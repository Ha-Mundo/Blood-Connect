import csv
from datetime import date, timedelta
from io import StringIO
from flask import abort
from app.extensions import db
from app.models import User, BloodDonation, BloodRequest
from app.services.email_service import EmailService


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
                    donation.status = "Approved"

                req.status = "Cancelled"

        db.session.commit()

        status_text = (
            "banned and your active records cleared"
            if not user.is_active
            else "activated"
        )

        return user, status_text
    
    # ===================== DONATIONS =====================
    @staticmethod
    def get_donations_page(page, search=None, blood_group=None, status=None, per_page=10):
        query = BloodDonation.query

        if search:
            search = search.strip().lower()
            query = query.filter(
                (BloodDonation.name.contains(search)) |
                (BloodDonation.email.contains(search)) |
                (BloodDonation.city.contains(search))
            )

        if blood_group:
            query = query.filter_by(blood_groups=blood_group.lower())

        if status:
            query = query.filter_by(status=status)

        pagination = query.order_by(BloodDonation.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        count = query.count()

        matches = {}

        claimed = [d for d in pagination.items if d.status == "Claimed"]

        if claimed:
            emails = [d.email for d in claimed]

            requests = BloodRequest.query.filter(
                BloodRequest.donor_email.in_(emails),
                BloodRequest.status.in_(["Pending", "Approved"])
            ).all()

            request_map = {
                (req.donor_email, req.blood_groups): req
                for req in requests
            }

            for d in claimed:
                key = (d.email, d.blood_groups)
                if key in request_map:
                    matches[d.id] = request_map[key]

        return pagination, count, matches

    # ===================== STATUS UPDATE =====================
    @staticmethod
    def update_donation_status(donation_id, new_status):
        donation = db.session.get(BloodDonation, donation_id)

        if not donation:
            return "Donation not found.", None

        allowed_statuses = [
            "Pending", "Claimed", "Approved",
            "Completed", "Unsuccessful", "Cancelled"
        ]

        if new_status not in allowed_statuses:
            return "Invalid status update.", None
        
        donation.status = new_status
        db.session.commit()

        if new_status == "Completed":
            try:
                EmailService.send_thank_you_email(
                    email=donation.email,
                    name=donation.name,
                    type_="donation"
                )
            except Exception:
                pass 
            
        return None, donation

    @staticmethod
    def update_request_status(request_id, new_status):
        blood_req = db.session.get(BloodRequest, request_id)

        if not blood_req:
            return "Request not found.", None

        allowed_statuses = ['Pending', 'Approved', 'Completed', 'Unsuccessful', 'Cancelled']

        if new_status not in allowed_statuses:
            return "Invalid status update.", None

        donation = BloodDonation.query.filter_by(
            email=blood_req.donor_email,
            blood_groups=blood_req.blood_groups,
            status='Claimed'
        ).first()

        # --- SYNCHRONIZATION LOGIC ---
        if new_status in ['Cancelled', 'Unsuccessful']:
            if donation:
                donation.status = 'Pending'

        elif new_status == 'Completed':
            if donation:
                donation.status = 'Completed'

        blood_req.status = new_status
        db.session.commit()

        if new_status == "Completed":
            try: 
                EmailService.send_thank_you_email(
                    email=blood_req.requester_email,
                    name=blood_req.name,
                    type_="request"
                )
            except Exception:
                pass 

        return None, blood_req

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

        return si.getvalue(), f"{table_type}.csv"

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