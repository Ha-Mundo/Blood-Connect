import datetime
from app.extensions import db
from app.models import BloodDonation, BloodRequest
from app.time_limit import is_action_allowed, threshold_donation, threshold_request


class BloodService:

    # -------------------
    # DONATION
    # -------------------
    @staticmethod
    def get_latest_donation(email):
        return BloodDonation.query.filter_by(email=email)\
            .order_by(BloodDonation.id.desc()).first()

    @staticmethod
    def get_active_donation(latest_donation, today, force_form):
        if not latest_donation or force_form:
            return None

        if latest_donation.status in ['Pending', 'Claimed', 'Cancelled', 'Unsuccessful']:
            return latest_donation

        if latest_donation.status == 'Approved' and not is_action_allowed(latest_donation.next_donation, today):
            return latest_donation

        return None

    @staticmethod
    def create_donation(form, user, latest_donation, today):
        THREE_MONTHS = datetime.timedelta(days=90)

        if form.age.data < 18:
            return None, "Legal requirement: You must be at least 18 years old to donate blood."

        if latest_donation and latest_donation.status == 'Approved':
            if not is_action_allowed(latest_donation.next_donation, today):
                return None, "Safety limit: You can only donate once every 90 days after a successful donation."
            
        if latest_donation:
            next_allowed_date = latest_donation.latest_donation + THREE_MONTHS
            
            if today < next_allowed_date:
                return None, (
                    f"You can donate again after {next_allowed_date.strftime('%d/%m/%Y')}."
                )
                

        new_donor = BloodDonation(
            name=form.name.data.lower(),
            age=form.age.data,
            blood_groups=form.blood_groups.data.lower(),
            city=form.city.data.lower(),
            email=form.email.data.lower(),
            latest_donation=today,
            next_donation=threshold_donation(today),
            donation_counter=(latest_donation.donation_counter + 1 if latest_donation else 1),
            status='Pending'
        )

        db.session.add(new_donor)
        db.session.commit()

        return new_donor, None

    @staticmethod
    def cancel_donation(donation, user_email):
        if donation.email == user_email and donation.status == 'Pending':
            db.session.delete(donation)
            db.session.commit()
            return True
        return False

    # -------------------
    # REQUEST
    # -------------------
    @staticmethod
    def get_latest_request(email):
        return BloodRequest.query.filter_by(requester_email=email)\
            .order_by(BloodRequest.id.desc()).first()

    @staticmethod
    def get_active_request(latest_request, force_form):
        if not latest_request or force_form:
            return None

        if latest_request.status in ['Pending', 'Approved', 'Unsuccessful']:
            return latest_request

        return None

    @staticmethod
    def search_donations(city, bg, page):
        pagination = BloodDonation.query.filter_by(
            blood_groups=bg.lower(),
            city=city.lower(),
            status='Approved'
        ).paginate(page=page, per_page=10, error_out=False)

        return pagination

    @staticmethod
    def cancel_request(blood_req, user_email):
        if blood_req.requester_email != user_email or blood_req.status != 'Pending':
            return False

        donation = BloodDonation.query.filter_by(
            email=blood_req.donor_email,
            blood_groups=blood_req.blood_groups,
            status='Claimed'
        ).first()

        if donation:
            donation.status = "Approved"

        blood_req.status = 'Cancelled'
        db.session.commit()

        return True

    @staticmethod
    def take_donation(donation, user):
        today = datetime.date.today()

        if donation.email == user.email:
            return None, "You cannot request your own donation!"

        last_request = BloodRequest.query.filter_by(
            requester_email=user.email
        ).order_by(BloodRequest.id.desc()).first()

        if last_request and last_request.status in ['Pending', 'Approved', 'Fulfilled']:
            allowed_date = threshold_request(last_request.request_date)

            if not is_action_allowed(allowed_date, today):
                return None, "Safety limit: You can only make one request every 7 days."

        new_request = BloodRequest(
            name=user.username.lower(),
            blood_groups=donation.blood_groups,
            city=donation.city,
            requester_email=user.email,
            donor_email=donation.email,
            request_date=today,
            status='Pending'
        )

        db.session.add(new_request)
        donation.status = 'Claimed'
        db.session.commit()

        return new_request, None