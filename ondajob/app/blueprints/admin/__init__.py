from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User, Job, Application, Report
from functools import wraps

admin_bp = Blueprint("admin", __name__, template_folder="templates")


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("Admin access required.", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_employers = User.query.filter_by(role="employer").count()
    total_jobs = Job.query.filter_by(status="active").count()
    total_applications = Application.query.count()
    pending_reports = Report.query.filter_by(status="pending").count()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    flagged_jobs = Job.query.join(Report, Report.job_id == Job.id)\
        .filter(Report.status == "pending").all()
    return render_template(
        "admin_dashboard.html",
        user=current_user,
        total_users=total_users,
        total_employers=total_employers,
        total_jobs=total_jobs,
        total_applications=total_applications,
        pending_reports=pending_reports,
        recent_users=recent_users,
        flagged_jobs=flagged_jobs,
    )


@admin_bp.route("/toggle-user/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    status = "activated" if user.is_active else "suspended"
    flash(f"User {user.full_name} has been {status}.", "success")
    return redirect(url_for("admin.dashboard"))
