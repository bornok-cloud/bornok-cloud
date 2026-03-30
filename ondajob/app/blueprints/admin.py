from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User, Job, Application, Report, Notification
from app.blueprints.auth import admin_required
from datetime import datetime, timedelta

admin_bp = Blueprint("admin", __name__, template_folder="../../templates")


@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    """Admin dashboard with system analytics"""
    # User statistics
    total_users = User.query.count()
    total_jobseekers = User.query.filter_by(role="jobseeker").count()
    total_employers = User.query.filter_by(role="employer").count()
    total_admins = User.query.filter_by(role="admin").count()
    
    # Job statistics
    total_jobs = Job.query.count()
    active_jobs = Job.query.filter_by(status="active").count()
    paused_jobs = Job.query.filter_by(status="paused").count()
    closed_jobs = Job.query.filter_by(status="closed").count()
    
    # Application statistics
    total_applications = Application.query.count()
    
    # Report statistics
    pending_reports = Report.query.filter_by(status="pending").count()
    
    # Recent registrations (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users_week = User.query.filter(User.created_at >= week_ago).count()
    
    # Recent data
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_applications = Application.query.order_by(Application.created_at.desc()).limit(5).all()
    
    return render_template(
        "admin_dashboard.html",
        user=current_user,
        total_users=total_users,
        total_jobseekers=total_jobseekers,
        total_employers=total_employers,
        total_admins=total_admins,
        total_jobs=total_jobs,
        active_jobs=active_jobs,
        paused_jobs=paused_jobs,
        closed_jobs=closed_jobs,
        total_applications=total_applications,
        pending_reports=pending_reports,
        new_users_week=new_users_week,
        recent_users=recent_users,
        recent_applications=recent_applications,
    )


@admin_bp.route("/users")
@admin_required
def users():
    """List all users with filtering"""
    role_filter = request.args.get("role", "")
    status_filter = request.args.get("status", "")
    page = request.args.get("page", 1, type=int)
    
    query = User.query
    
    # Filter by role
    if role_filter and role_filter in ["jobseeker", "employer", "admin"]:
        query = query.filter_by(role=role_filter)
    
    # Filter by status
    if status_filter == "active":
        query = query.filter_by(is_active=True)
    elif status_filter == "inactive":
        query = query.filter_by(is_active=False)
    
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template(
        "admin_users.html",
        users=pagination.items,
        pagination=pagination,
        role_filter=role_filter,
        status_filter=status_filter
    )


@admin_bp.route("/users/<int:user_id>")
@admin_required
def user_details(user_id):
    """View user details"""
    user = User.query.get_or_404(user_id)
    
    # Get additional statistics
    if user.role == "jobseeker":
        applications = Application.query.filter_by(user_id=user.id).all()
        stats = {
            "total_applications": len(applications),
            "applied": sum(1 for a in applications if a.status == "applied"),
            "reviewing": sum(1 for a in applications if a.status == "reviewing"),
            "interview": sum(1 for a in applications if a.status == "interview"),
            "offered": sum(1 for a in applications if a.status == "offered"),
            "rejected": sum(1 for a in applications if a.status == "rejected"),
        }
    elif user.role == "employer":
        jobs = Job.query.filter_by(employer_id=user.id).all()
        applications = Application.query.join(Job)\
            .filter(Job.employer_id == user.id).all()
        stats = {
            "total_jobs": len(jobs),
            "active_jobs": sum(1 for j in jobs if j.status == "active"),
            "total_applicants": len(applications),
        }
    else:
        stats = {}
    
    return render_template(
        "admin_user_details.html",
        user=user,
        stats=stats
    )


@admin_bp.route("/users/<int:user_id>/toggle-status", methods=["POST"])
@admin_required
def toggle_user_status(user_id):
    """Activate/suspend user"""
    user = User.query.get_or_404(user_id)
    
    # Prevent self-suspension
    if user.id == current_user.id:
        flash("You cannot suspend your own account.", "error")
        return redirect(request.referrer)
    
    try:
        user.is_active = not user.is_active
        db.session.commit()
        status = "activated" if user.is_active else "suspended"
        flash(f"User {user.full_name} has been {status}.", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while updating user status.", "error")
    
    return redirect(request.referrer or url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    """Delete a user account"""
    user = User.query.get_or_404(user_id)
    
    # Prevent self-deletion
    if user.id == current_user.id:
        flash("You cannot delete your own account.", "error")
        return redirect(request.referrer)
    
    try:
        # Delete all related data (cascaded by database)
        db.session.delete(user)
        db.session.commit()
        flash(f"User {user.full_name} has been deleted.", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the user.", "error")
    
    return redirect(request.referrer or url_for("admin.users"))


@admin_bp.route("/jobs")
@admin_required
def jobs():
    """List all jobs with filtering"""
    status_filter = request.args.get("status", "")
    industry_filter = request.args.get("industry", "")
    page = request.args.get("page", 1, type=int)
    
    query = Job.query
    
    # Filter by status
    if status_filter and status_filter in ["active", "paused", "closed"]:
        query = query.filter_by(status=status_filter)
    
    # Filter by industry
    if industry_filter:
        query = query.filter_by(industry=industry_filter)
    
    pagination = query.order_by(Job.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get industries for filter
    industries = db.session.query(Job.industry)\
        .filter(Job.industry.isnot(None))\
        .distinct()\
        .all()
    industries = [ind[0] for ind in industries]
    
    return render_template(
        "admin_jobs.html",
        jobs=pagination.items,
        pagination=pagination,
        status_filter=status_filter,
        industry_filter=industry_filter,
        industries=industries
    )


@admin_bp.route("/jobs/<int:job_id>/close", methods=["POST"])
@admin_required
def close_job(job_id):
    """Close a job listing"""
    job = Job.query.get_or_404(job_id)
    
    try:
        job.status = "closed"
        db.session.commit()
        flash(f"Job '{job.title}' has been closed.", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while closing the job.", "error")
    
    return redirect(request.referrer or url_for("admin.jobs"))


@admin_bp.route("/reports")
@admin_required
def reports():
    """List all reports"""
    status_filter = request.args.get("status", "")
    page = request.args.get("page", 1, type=int)
    
    query = Report.query
    
    # Filter by status
    if status_filter and status_filter in ["pending", "reviewed", "resolved"]:
        query = query.filter_by(status=status_filter)
    
    pagination = query.order_by(Report.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template(
        "admin_reports.html",
        reports=pagination.items,
        pagination=pagination,
        status_filter=status_filter
    )


@admin_bp.route("/reports/<int:report_id>")
@admin_required
def report_details(report_id):
    """View report details"""
    report = Report.query.get_or_404(report_id)
    
    return render_template("admin_report_details.html", report=report)


@admin_bp.route("/reports/<int:report_id>/resolve", methods=["POST"])
@admin_required
def resolve_report(report_id):
    """Resolve a report"""
    report = Report.query.get_or_404(report_id)
    action = request.form.get("action", "")
    
    try:
        report.status = "resolved"
        
        # Take action based on report type
        if action == "close_job" and report.job_id:
            job = Job.query.get(report.job_id)
            if job:
                job.status = "closed"
        elif action == "suspend_user" and report.user_id:
            user = User.query.get(report.user_id)
            if user:
                user.is_active = False
        
        db.session.commit()
        flash("Report resolved successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while resolving the report.", "error")
    
    return redirect(request.referrer or url_for("admin.reports"))
