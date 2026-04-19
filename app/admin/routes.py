""" Admin Dashboard and Management Blueprint """
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, Response, current_app
from flask_login import current_user
from flask_mail import Message

from app.extensions import mail
from app.services.admin_service import AdminService

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.before_request
def require_admin():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login", next=request.url))

    if current_user.role != "admin":
        abort(403)


# ===================== USERS =====================

@admin_bp.route("/users")
def users_db():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search")
    status = request.args.get("status")
    verified = request.args.get("verified")

    pagination, count = AdminService.get_users_page(
        page=page,
        search=search,
        status=status,
        verified=verified
    )

    return render_template(
        "users_db.html",
        pagination=pagination,
        all_users_counter=count
    )


# ===================== DONATIONS =====================

@admin_bp.route("/donations")
def donations_db():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search")
    blood_group = request.args.get("blood_group")
    status = request.args.get("status")

    pagination, count, matches = AdminService.get_donations_page(
        page=page,
        search=search,
        blood_group=blood_group,
        status=status
    )

    return render_template(
        "donations_db.html",
        pagination=pagination,
        all_donations_counter=count,
        matches=matches
    )


# ===================== REQUESTS =====================

@admin_bp.route("/requests")
def requests_db():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search")
    blood_group = request.args.get("blood_group")
    status = request.args.get("status")

    pagination, count, donor_names = AdminService.get_requests_page(
        page=page,
        search=search,
        blood_group=blood_group,
        status=status
    )

    return render_template(
        "requests_db.html",
        pagination=pagination,
        all_requests_counter=count,
        donor_names=donor_names
    )


# ===================== STATUS UPDATES =====================
@admin_bp.route("/update_donation_status/<int:id>", methods=["POST"])
def update_donation_status(id):
    new_status = request.form.get("new_status")

    if not new_status:
        abort(400)

    error, donation = AdminService.update_donation_status(id, new_status)

    if error:
        flash(error, "danger")
    else:
        if new_status == "Approved":
            try:
                msg = Message(
                    "Blood Donation Approved",
                    sender=current_app.config["MAIL_DEFAULT_SENDER"],
                    recipients=[donation.email],
                )
                msg.body = (
                    f"Hello {donation.name.capitalize()},\n\n"
                    f"Great news! Your blood donation has been Approved. "
                    f"Thank you for your contribution to the community."
                )
                mail.send(msg)
            except Exception:
                flash("Status updated, but email notification failed to send.", "warning")

        flash(f"Donation #{id} updated to {new_status}.", "success")

    return redirect(request.referrer or url_for("admin.donations_db"))

@admin_bp.route("/update_request_status/<int:id>", methods=["POST"])
def update_request_status(id):
    AdminService.update_request_status(id)
    flash("Request status updated.", "success")
    return redirect(request.referrer or url_for("admin.requests_db"))


@admin_bp.route("/update_users_status/<int:user_id>", methods=["POST"])
def toggle_user(user_id):
    user, message = AdminService.toggle_user(user_id)

    if not user:
        flash(message, "danger")
        return redirect(request.referrer or url_for("admin.users_db"))

    try:
        msg = Message(
            f"Account Update - Blood Donation System",
            sender=current_app.config["MAIL_DEFAULT_SENDER"],
            recipients=[user.email],
        )
        msg.body = (
            f"Hello {user.username},\n\n"
            f"Your account status has been updated.\n\n"
            f"{message}"
        )
        mail.send(msg)
    except Exception:
        flash("User updated, but email notification failed.", "warning")

    flash(f"User {user.username}: {message}", "success")
    return redirect(request.referrer or url_for("admin.users_db"))


# ===================== EXPORT =====================

@admin_bp.route("/export_csv/<table_type>")
def export_csv(table_type):
    try:
        csv_data, filename = AdminService.build_csv(table_type)
    except ValueError:
        abort(404)

    output = Response(csv_data, mimetype="text/csv")
    output.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return output


# ===================== CLEANUP =====================

@admin_bp.route("/cleanup_records", methods=["POST"])
def cleanup_records():
    deleted_donations, deleted_requests = AdminService.cleanup_records()

    flash(
        f"Database optimized. Removed {deleted_donations} donations and {deleted_requests} requests.",
        "info"
    )

    return redirect(url_for("main.profile"))