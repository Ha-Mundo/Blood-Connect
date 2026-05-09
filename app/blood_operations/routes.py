from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
import datetime

from app.models import BloodDonation, BloodRequest
from app.forms import DonationForm, RequestForm
from app.services.blood_service import BloodService

blood_ops_bp = Blueprint('blood_ops', __name__)


@blood_ops_bp.route("/blood_donation", methods=['GET', 'POST'])
@login_required
def blood_donation():
    today = datetime.date.today()
    latest_donation = BloodService.get_latest_donation(current_user.email)

    force_form = request.args.get('new') == '1'
    active_donation = BloodService.get_active_donation(current_user, latest_donation, today, force_form)

    form = DonationForm()

    if request.method == 'GET':
        form.name.data = current_user.username.title()
        form.email.data = current_user.email
        if current_user.blood_group:
            form.blood_groups.data = current_user.blood_group.upper()

    if form.validate_on_submit() and not active_donation:
        donation, error = BloodService.create_donation(
            form, current_user, latest_donation, today
        )

        if error:
            flash(error, "danger")
            return render_template('donate.html', form=form)

        flash("Thank you! Your donation offer has been registered.", "success")
        return redirect(url_for('blood_ops.blood_donation'))

    return render_template('donate.html', form=form, active_donation=active_donation)


@blood_ops_bp.route("/cancel_donation/<int:id>", methods=['POST'])
@login_required
def cancel_donation(id):
    donation = BloodDonation.query.get_or_404(id)

    if BloodService.cancel_donation(donation, current_user.email):
        flash("Your donation has been cancelled.", "info")
    else:
        flash("Action not allowed.", "danger")

    return redirect(url_for('blood_ops.blood_donation'))


@blood_ops_bp.route("/blood_request", methods=['GET', 'POST'])
@login_required
def blood_request():
    latest_request = BloodService.get_latest_request(current_user.email)

    force_form = request.args.get('new') == '1'
    active_request = BloodService.get_active_request(latest_request, force_form)

    form = RequestForm()

    if request.method == 'GET' and not active_request:
        form.name.data = current_user.username.title()
        form.email.data = current_user.email
        if current_user.blood_group:
            form.blood_groups.data = current_user.blood_group.upper()

    if form.validate_on_submit() and not active_request:
        r_city = (form.city.data or "").lower()
        r_bg = (form.blood_groups.data or "").lower()

        return redirect(url_for('blood_ops.blood_request', city=r_city, bg=r_bg))

    if active_request:
        return render_template('find_blood.html', form=form, active_request=active_request)

    city = request.args.get('city')
    bg = request.args.get('bg')

    if city and bg:
        page = request.args.get('page', 1, type=int)
        pagination = BloodService.search_donations(city, bg, page)

        if not pagination.items:
            return render_template('empty_db.html')

        return render_template('results.html', pagination=pagination, city=city, bg=bg)

    return render_template('find_blood.html', form=form, active_request=None)


@blood_ops_bp.route("/cancel_request/<int:id>", methods=['POST'])
@login_required
def cancel_request(id):
    blood_req = BloodRequest.query.get_or_404(id)

    if BloodService.cancel_request(blood_req, current_user.email):
        flash("Blood request cancelled. The donation is now available for others.", "info")
    else:
        flash("Action not allowed.", "danger")

    return redirect(url_for('blood_ops.blood_request'))


@blood_ops_bp.route("/take_donation", methods=['POST'])
@login_required
def take_donation():
    donation_id = request.form.get('id')
    donation = BloodDonation.query.get_or_404(donation_id)

    result, error = BloodService.take_donation(donation, current_user)

    if error:
        flash(error, "danger" if "Safety" in error else "warning")
        return redirect(url_for('main.home'))

    flash("Request successful! Notification sent.", "success")
    return redirect(url_for('blood_ops.blood_request'))