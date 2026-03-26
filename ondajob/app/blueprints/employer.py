from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Job, Application, Company

employer_bp = Blueprint("employer", __name__, template_folder="../../templates")


@employer_bp.route("/dashboard")
@login_required
def dashboard():
    company = Company.query.filter_by(user_id=current_user.id).first()
    jobs = Job.query.filter_by(employer_id=current_user.id)\
        .order_by(Job.created_at.desc()).all()
    total_applicants = sum(j.applications.count() for j in jobs)
    total_views = sum(j.views_count for j in jobs)
    recent_applicants = Application.query.join(Job)\
        .filter(Job.employer_id == current_user.id)\
        .order_by(Application.created_at.desc()).limit(5).all()
    return render_template(
        "employer_dashboard.html",
        user=current_user,
        company=company,
        jobs=jobs,
        total_applicants=total_applicants,
        total_views=total_views,
        recent_applicants=recent_applicants,
    )


@employer_bp.route("/post-job", methods=["POST"])
@login_required
def post_job():
    company = Company.query.filter_by(user_id=current_user.id).first()
    job = Job(
        employer_id=current_user.id,
        company_id=company.id if company else None,
        title=request.form.get("title", ""),
        description=request.form.get("description", ""),
        location=request.form.get("location", ""),
        job_type=request.form.get("job_type", "full-time"),
        work_setup=request.form.get("work_setup", "on-site"),
        experience_level=request.form.get("experience_level", "mid"),
        salary_min=int(request.form.get("salary_min", 0) or 0),
        salary_max=int(request.form.get("salary_max", 0) or 0),
        skills_required=request.form.get("skills", ""),
        industry=request.form.get("industry", ""),
    )
    db.session.add(job)
    db.session.commit()
    flash("Job posted successfully!", "success")
    return redirect(url_for("employer.dashboard"))
