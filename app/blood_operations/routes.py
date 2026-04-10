""" Donations and Requests Blueprint """
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
import datetime

from app.extensions import db
from app.models import BloodDonation, BloodRequest
from app.forms import DonationForm, RequestForm
from app.time_limit import is_action_allowed, threshold_donation, threshold_request

blood_ops_bp = Blueprint('blood_ops', __name__)

@blood_ops_bp.route("/blood_donation", methods=['GET', 'POST'])
@login_required
def donate_blood():
    """ Register a new donation or view current donation status """
    today = datetime.date.today()
    latest_donation = BloodDonation.query.filter_by(email=current_user.email).order_by(BloodDonation.id.desc()).first()
    
    # Check if user explicitly clicked 'Make a new donation attempt'
    force_form = request.args.get('new') == '1'
    active_donation = None
    
    if latest_donation and not force_form:
        # Show status for ongoing, cancelled, or unsuccessful donations
        if latest_donation.status in ['Pending', 'Claimed', 'Cancelled', 'Unsuccessful']:
            active_donation = latest_donation
        # Enforce cooldown ONLY if the previous one was successfully completed
        elif latest_donation.status == 'Approved' and not is_action_allowed(latest_donation.next_donation, today):
            active_donation = latest_donation

    form = DonationForm()
    # SELF-COMPILE FORM
    if request.method == 'GET':
        form.name.data = current_user.username.title()
        form.email.data = current_user.email
        if current_user.blood_group:
            # Convert to uppercase to match the BLOOD_CHOICES in forms.py
            form.blood_groups.data = current_user.blood_group.upper()
    
    if form.validate_on_submit() and not active_donation:
        # Age validation check
        if form.age.data < 18:
            flash("Legal requirement: You must be at least 18 years old to donate blood.", "danger")
            return render_template('donate.html', form=form, active_donation=None)
        
        email = form.email.data.lower()
        
        # Double-check cooldown for Approved donations at the logic level
        if latest_donation and latest_donation.status == 'Approved' and not is_action_allowed(latest_donation.next_donation, today):
            flash("Safety limit: You can only donate once every 90 days after a successful donation.", "danger")
            return redirect(url_for('blood_ops.donate_blood'))

        new_donor = BloodDonation(
            name=form.name.data.lower(), 
            age=form.age.data,
            blood_groups=form.blood_groups.data.lower(), 
            city=form.city.data.lower(),
            email=email, 
            latest_donation=today, 
            next_donation=threshold_donation(today),
            donation_counter=(latest_donation.donation_counter + 1 if latest_donation else 1),
            status='Pending'
        )
        db.session.add(new_donor)
        db.session.commit()
        
        flash("Thank you! Your donation offer has been registered.", "success")
        return redirect(url_for('blood_ops.blood_donation'))
        
    return render_template('donate.html', form=form)

@blood_ops_bp.route("/cancel_donation/<int:id>", methods=['POST'])
@login_required
def cancel_donation(id):
    """ Allow users to cancel their own pending donations """
    donation = BloodDonation.query.get_or_404(id)
    # Security check: ensure the user owns this donation and it's pending
    if donation.email == current_user.email and donation.status == 'Pending':
        db.session.delete(donation) # we remove the record from the database
        db.session.commit()
        flash("Your donation has been cancelled.", "info")
    else:
        flash("Action not allowed.", "danger")
        
    return redirect(url_for('blood_ops.blood_donation'))

@blood_ops_bp.route("/blood_request", methods=['GET', 'POST'])
@login_required
def blood_request():
    """ Search for donors. Database logging is handled by 'take_donation' upon selection. """
    
    # 1. Fetch the user's most recent request to check for active/pending status
    latest_request = BloodRequest.query.filter_by(requester_email=current_user.email).order_by(BloodRequest.id.desc()).first()
    
    force_form = request.args.get('new') == '1'
    active_request = None
    
    # Logic to lock the UI if a request is already in progress
    if latest_request and not force_form:
        if latest_request.status in ['Pending', 'Approved', 'Unsuccessful']:
            active_request = latest_request
            
    form = RequestForm()
    
    # PRE-FILL FORM FROM PROFILE (GET requests only)
    if request.method == 'GET' and not active_request:
        form.name.data = current_user.username.title()
        form.email.data = current_user.email
        if current_user.blood_group:
            form.blood_groups.data = current_user.blood_group.upper()
            
    # FORM SUBMISSION: We only redirect to the search view, no DB insertion here!
    if form.validate_on_submit() and not active_request:
        # Safe extraction to prevent AttributeError if fields are disabled/empty
        r_city = (form.city.data or "").lower()
        r_bg = (form.blood_groups.data or "").lower()
        
        # Redirect to the same route with GET parameters to trigger the search logic below
        return redirect(url_for('blood_request', city=r_city, bg=r_bg))
    
    # If there is an active request record, show the status view instead of the search
    if active_request:
        return render_template('find_blood.html', form=form, active_request=active_request)

    # SEARCH LOGIC: Triggered by GET parameters (city and bg)
    city = request.args.get('city')
    bg = request.args.get('bg')
    
    if city and bg:
        page = request.args.get('page', 1, type=int)
        
        # Search for donors with 'Approved' status matching the criteria
        pagination = BloodDonation.query.filter_by(
            blood_groups=bg.lower(),
            city=city.lower(),
            status='Approved' 
        ).paginate(page=page, per_page=10, error_out=False)
        
        # Show empty state if no donors are found
        if not pagination.items:
            return render_template('empty_db.html')
            
        # Pass results to the template where the user can finally trigger 'take_donation'
        return render_template('results.html', pagination=pagination, city=city, bg=bg)
                               
    return render_template('find_blood.html', form=form, active_request=None)

@blood_ops_bp.route("/cancel_request/<int:id>", methods=['POST'])
@login_required
def cancel_request(id):
    """ Soft cancel the request and free up the claimed donation """
    blood_req = BloodRequest.query.get_or_404(id)
    
    if blood_req.requester_email == current_user.email and blood_req.status == 'Pending':
        
        # 1. Find the claimed donation and make it available again
        donation = BloodDonation.query.filter_by(
            email=blood_req.donor_email, 
            blood_groups=blood_req.blood_groups,
            status='Claimed'
        ).first()
        
        if donation:
            donation.status = 'Pending'
            
        # 2. Soft Delete we update the status to cancelled
        blood_req.status = 'Cancelled'
        db.session.commit()
        
        flash("Blood request cancelled. The donation is now available for others.", "info")
    else:
        flash("Action not allowed.", "danger")
        
    return redirect(url_for('blood_ops.blood_request'))

@blood_ops_bp.route("/take_donation", methods=['POST'])
@login_required
def take_donation():
    """ Process a blood request and change donation status instead of deleting """
    donation_id = request.form.get('id')
    donation = BloodDonation.query.get_or_404(donation_id)
    today = datetime.date.today()

    if donation.email == current_user.email:
        flash("You cannot request your own donation!", "warning")
        return redirect(url_for('home'))

    # Apply limit ONLY if last request is active or successful
    last_request = BloodRequest.query.filter_by(requester_email=current_user.email).order_by(BloodRequest.id.desc()).first()
    if last_request and last_request.status in ['Pending', 'Approved', 'Fulfilled']:
        allowed_date = threshold_request(last_request.request_date)
        if not is_action_allowed(allowed_date, today):
            flash("Safety limit: You can only make one request every 7 days.", "danger")
            return redirect(url_for('home'))
    
    new_request = BloodRequest(
        name=current_user.username.lower(),
        blood_groups=donation.blood_groups,
        city=donation.city,
        requester_email=current_user.email,  
        donor_email=donation.email,          
        request_date=today,
        status='Pending'
    )
    
    db.session.add(new_request)
    donation.status = 'Claimed'
    db.session.commit()
    
    flash("Request successful! Notification sent.", "success")
    return redirect(url_for('blood_ops.blood_request'))