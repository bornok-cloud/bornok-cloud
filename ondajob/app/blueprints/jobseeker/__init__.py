from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Application, Job, SavedJob

jobseeker_bp = Blueprint("jobseeker", __name__, template_folder="templates")


@jobseeker_bp.route("/dashboard")
@login_required
def dashboard():
    applications = Application.query.filter_by(user_id=current_user.id)\
        .order_by(Application.created_at.desc()).limit(5).all()
    saved_count = SavedJob.query.filter_by(user_id=current_user.id).count()
    app_count = Application.query.filter_by(user_id=current_user.id).count()
    interview_count = Application.query.filter_by(
        user_id=current_user.id, status="interview"
    ).count()
    recommended_jobs = Job.query.filter_by(status="active")\
        .order_by(Job.created_at.desc()).limit(4).all()
    return render_template(
        "jobseeker_dashboard.html",
        user=current_user,
        applications=applications,
        saved_count=saved_count,
        app_count=app_count,
        interview_count=interview_count,
        recommended_jobs=recommended_jobs,
    )
