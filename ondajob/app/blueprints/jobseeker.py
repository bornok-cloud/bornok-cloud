from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Application, Job, SavedJob, Profile, Notification, Interview
from datetime import datetime

jobseeker_bp = Blueprint("jobseeker", __name__, template_folder="../../templates")


@jobseeker_bp.route("/dashboard")
@login_required
def dashboard():
    """Jobseeker dashboard with real data"""
    # Get user's applications
    user_applications = Application.query.filter_by(user_id=current_user.id).all()
    
    # Get user's interviews (from applications in interview status)
    user_interviews = Interview.query.join(Application).filter(
        Application.user_id == current_user.id
    ).all()
    
    # Get user's saved jobs
    user_saved_jobs = SavedJob.query.filter_by(user_id=current_user.id).all()
    
    # Get total available jobs
    total_jobs_available = Job.query.filter_by(status="active").count()
    
    # Get user profile
    user_profile = Profile.query.filter_by(user_id=current_user.id).first()
    
    # Calculate profile completion percentage
    profile_completion_percent = 0
    if user_profile:
        fields_filled = 0
        total_fields = 8
        if user_profile.title: fields_filled += 1
        if user_profile.summary: fields_filled += 1
        if user_profile.location: fields_filled += 1
        if user_profile.skills: fields_filled += 1
        if user_profile.linkedin_url: fields_filled += 1
        if user_profile.portfolio_url: fields_filled += 1
        if user_profile.experience_years: fields_filled += 1
        if user_profile.resume_score: fields_filled += 1
        profile_completion_percent = int((fields_filled / total_fields) * 100)
    
    # Get unread notifications
    unread_notifications = Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).count()
    
    # Recommended jobs (recently posted active jobs)
    recommended_jobs = Job.query.filter_by(status="active")\
        .order_by(Job.created_at.desc()).limit(4).all()
    
    return render_template(
        "jobseeker_dashboard.html",
        user=current_user,
        user_applications=user_applications,
        user_interviews=user_interviews,
        user_saved_jobs=user_saved_jobs,
        user_profile=user_profile,
        profile_completion_percent=profile_completion_percent,
        unread_notifications=unread_notifications,
        total_jobs_available=total_jobs_available,
        recommended_jobs=recommended_jobs,
        now=datetime.utcnow
    )
