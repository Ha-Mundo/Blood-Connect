""" Admin Dashboard and Management Blueprint """
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, Response
from flask_login import login_required, current_user

import csv
from io import StringIO
from datetime import datetime, timedelta

from flask_mail import Message

from app.extensions import db, mail, limiter
from app.models import User, BloodDonation, BloodRequest

# Prefix all routes with /admin automatically
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
@limiter.exempt
def require_admin():
    """ DRY approach: Enforce admin access for the entire blueprint """
    if current_user.role != 'admin':
        abort(403) # Let the global error handler in main_bp take over

@admin_bp.route("/users")
def users_db():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search')
    status = request.args.get('status')
    verified = request.args.get('verified')

    # Base query
    query = User.query

    # Apply Search (Username or Email)
    if search:
        query = query.filter((User.username.contains(search)) | (User.email.contains(search)))

    # Apply Status Filter (Active/Banned)
    if status:
        is_active = True if status == 'active' else False
        query = query.filter_by(is_active=is_active)

    # Apply Verification Filter
    if verified in ['1', '0']:
        is_verified = True if verified == '1' else False
        query = query.filter_by(is_verified=is_verified)

    pagination = query.order_by(User.id.desc()).paginate(page=page, per_page=10, error_out=False)
    count = query.count()
    
    return render_template('users_db.html', pagination=pagination, all_users_counter=count)

@admin_bp.route("/donations")
def donations_db():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search')
    status = request.args.get('status')
    verified = request.args.get('verified')

    # Base query
    query = User.query

    # Apply Search (Username or Email)
    if search:
        query = query.filter((User.username.contains(search)) | (User.email.contains(search)))

    # Apply Status Filter (Active/Banned)
    if status:
        is_active = True if status == 'active' else False
        query = query.filter_by(is_active=is_active)

    # Apply Verification Filter
    if verified in ['1', '0']:
        is_verified = True if verified == '1' else False
        query = query.filter_by(is_verified=is_verified)

    pagination = query.order_by(User.id.desc()).paginate(page=page, per_page=10, error_out=False)
    count = query.count()
    
    return render_template('users_db.html', pagination=pagination, all_users_counter=count)

@admin_bp.route("/requests")
def request_db():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search')
    blood_group = request.args.get('blood_group')
    status = request.args.get('status')

    # Base query
    query = BloodRequest.query

    # Apply Search (Name, Requester Email, or City)
    if search:
        search_term = search.lower()
        query = query.filter(
            (BloodRequest.name.contains(search_term)) | 
            (BloodRequest.requester_email.contains(search_term)) |
            (BloodRequest.city.contains(search_term))
        )

    # Apply Blood Group Filter
    if blood_group:
        query = query.filter_by(blood_groups=blood_group.lower())

    # Apply Status Filter
    if status:
        query = query.filter_by(status=status)

    # Paginate and count filtered records
    pagination = query.order_by(BloodRequest.id.desc()).paginate(page=page, per_page=10, error_out=False)
    count = query.count()
    
    # Create a mapping of donor emails to names
    donor_names = {}
    emails_to_fetch = [req.donor_email for req in pagination.items if req.donor_email]
    
    if emails_to_fetch:
        # Fetch donors matching the emails in the current pagination view
        donors = BloodDonation.query.filter(BloodDonation.email.in_(emails_to_fetch)).all()
        # Map email -> name (e.g., {"donor@mail.com": "John Doe"})
        donor_names = {d.email: d.name for d in donors}
    
    return render_template('request_db.html', 
                           pagination=pagination, 
                           all_requests_counter=query.count(),
                           donor_names=donor_names) # Pass the dictionary to the template

@admin_bp.route("/update_donation_status/<int:id>", methods=['POST'])
def update_donation_status(id):
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search')
    blood_group = request.args.get('blood_group')
    status = request.args.get('status')

    # Base query
    query = BloodRequest.query

    # Apply Search (Name, Requester Email, or City)
    if search:
        search_term = search.lower()
        query = query.filter(
            (BloodRequest.name.contains(search_term)) | 
            (BloodRequest.requester_email.contains(search_term)) |
            (BloodRequest.city.contains(search_term))
        )

    # Apply Blood Group Filter
    if blood_group:
        query = query.filter_by(blood_groups=blood_group.lower())

    # Apply Status Filter
    if status:
        query = query.filter_by(status=status)

    # Paginate and count filtered records
    pagination = query.order_by(BloodRequest.id.desc()).paginate(page=page, per_page=10, error_out=False)
    count = query.count()
    
    # Create a mapping of donor emails to names
    donor_names = {}
    emails_to_fetch = [req.donor_email for req in pagination.items if req.donor_email]
    
    if emails_to_fetch:
        # Fetch donors matching the emails in the current pagination view
        donors = BloodDonation.query.filter(BloodDonation.email.in_(emails_to_fetch)).all()
        # Map email -> name (e.g., {"donor@mail.com": "John Doe"})
        donor_names = {d.email: d.name for d in donors}
    
    return render_template('request_db.html', 
                           pagination=pagination, 
                           all_requests_counter=query.count(),
                           donor_names=donor_names) # Pass the dictionary to the template

@admin_bp.route("/update_request_status/<int:id>", methods=['POST'])
def update_request_status(id):
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search')
    blood_group = request.args.get('blood_group')
    status = request.args.get('status')

    # Base query
    query = BloodRequest.query

    # Apply Search (Name, Requester Email, or City)
    if search:
        search_term = search.lower()
        query = query.filter(
            (BloodRequest.name.contains(search_term)) | 
            (BloodRequest.requester_email.contains(search_term)) |
            (BloodRequest.city.contains(search_term))
        )

    # Apply Blood Group Filter
    if blood_group:
        query = query.filter_by(blood_groups=blood_group.lower())

    # Apply Status Filter
    if status:
        query = query.filter_by(status=status)

    # Paginate and count filtered records
    pagination = query.order_by(BloodRequest.id.desc()).paginate(page=page, per_page=10, error_out=False)
    count = query.count()
    
    # Create a mapping of donor emails to names
    donor_names = {}
    emails_to_fetch = [req.donor_email for req in pagination.items if req.donor_email]
    
    if emails_to_fetch:
        # Fetch donors matching the emails in the current pagination view
        donors = BloodDonation.query.filter(BloodDonation.email.in_(emails_to_fetch)).all()
        # Map email -> name (e.g., {"donor@mail.com": "John Doe"})
        donor_names = {d.email: d.name for d in donors}
    
    return render_template('request_db.html', 
                           pagination=pagination, 
                           all_requests_counter=query.count(),
                           donor_names=donor_names) # Pass the dictionary to the template
    
@admin_bp.route("/update_users_status/<int:user_id>", methods=['POST'])
def toggle_user(user_id):
    """ Admin only: Ban/Unban users, cleanup records, and notify user """
    if current_user.role != 'admin':
        abort(403)
    
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash("You cannot ban another administrator!", "danger")
    else:
        user.is_active = not user.is_active
        
        # If the user is being banned, cleanup their active interactions
        if not user.is_active:
            BloodDonation.query.filter_by(email=user.email, status='Pending').update({'status': 'Cancelled'})
            
            pending_requests = BloodRequest.query.filter_by(requester_email=user.email, status='Pending').all()
            for req in pending_requests:
                donation = BloodDonation.query.filter_by(
                    email=req.donor_email, 
                    blood_groups=req.blood_groups,
                    status='Claimed'
                ).first()
                if donation:
                    donation.status = 'Pending'
                req.status = 'Cancelled'
        
        db.session.commit()
        
        # Send email notification regarding account status
        action = "suspended" if not user.is_active else "reactivated"
        try:
            msg = Message(f"Account {action.capitalize()} - Blood Donation System", 
                          sender=app.config['MAIL_DEFAULT_SENDER'], 
                          recipients=[user.email])
            msg.body = f"Hello {user.username},\n\nYour account has been {action} by an administrator. If you believe this is an error, please contact support."
            mail.send(msg)
        except Exception as e:
            flash("User updated, but email notification failed to send.", "warning")

        status = "banned and their active records cleared" if not user.is_active else "activated"
        flash(f"User {user.username} has been {status}.", "success")
    
    return redirect(request.referrer or url_for('all_users_db'))

@admin_bp.route("/export_csv/<table_type>")
def export_csv(table_type):
    si = StringIO()
    cw = csv.writer(si)

    if table_type == 'donations':
        records = BloodDonation.query.all()
        cw.writerow(['ID', 'Name', 'Email', 'Age', 'Blood Group', 'City', 'Status', 'Latest Donation', 'Next Donation'])
        for r in records:
            cw.writerow([r.id, r.name, r.email, r.age, r.blood_groups, r.city, r.status, r.latest_donation, r.next_donation])
        filename = "donations_export.csv"

    elif table_type == 'requests':
        records = BloodRequest.query.all()
        cw.writerow(['ID', 'Recipient Name', 'Requester Email', 'Blood Group', 'City', 'Status', 'Request Date'])
        for r in records:
            cw.writerow([r.id, r.name, r.requester_email, r.blood_groups, r.city, r.status, r.request_date])
        filename = "requests_export.csv"
    else:
        abort(404)

    output = Response(si.getvalue(), mimetype="text/csv")
    output.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return output

@admin_bp.route("/cleanup_records", methods=['POST'])
def cleanup_records():
    """ Admin only: Delete Cancelled and Unsuccessful records older than 30 days """
    # Safety logic: We only delete failed/cancelled transactions, keeping the successful history.
    threshold_date = datetime.date.today() - timedelta(days=30)
    
    deleted_donations = BloodDonation.query.filter(
        BloodDonation.status.in_(['Cancelled', 'Unsuccessful']),
        BloodDonation.latest_donation < threshold_date
    ).delete(synchronize_session=False)
    
    deleted_requests = BloodRequest.query.filter(
        BloodRequest.status.in_(['Cancelled', 'Unsuccessful']),
        BloodRequest.request_date < threshold_date
    ).delete(synchronize_session=False)
    
    db.session.commit()
    flash(f"Database optimized. Removed {deleted_donations} old donations and {deleted_requests} old requests.", "info")
    
    return redirect(url_for('main.profile'))