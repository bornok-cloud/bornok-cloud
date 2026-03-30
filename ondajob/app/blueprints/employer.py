from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Job, Application, Company, User
from app.blueprints.auth import employer_required

employer_bp = Blueprint("employer", __name__, template_folder="../../templates")


@employer_bp.route("/dashboard")
@employer_required
def dashboard():
    """Employer dashboard with analytics"""
    company = Company.query.filter_by(user_id=current_user.id).first()
    jobs = Job.query.filter_by(employer_id=current_user.id)\
        .order_by(Job.created_at.desc()).all()
    
    # Calculate analytics
    total_applicants = sum(j.applications.count() for j in jobs)
    total_views = sum(j.views_count or 0 for j in jobs)
    active_jobs = sum(1 for j in jobs if j.status == "active")
    
    # Get application status breakdown
    all_applications = Application.query.join(Job)\
        .filter(Job.employer_id == current_user.id).all()
    
    status_breakdown = {}
    for app in all_applications:
        status = app.status
        status_breakdown[status] = status_breakdown.get(status, 0) + 1
    
    # Recent applicants
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
        active_jobs=active_jobs,
        status_breakdown=status_breakdown,
        recent_applicants=recent_applicants,
    )


@employer_bp.route("/post-job", methods=["GET", "POST"])
@employer_required
def post_job():
    """Create a new job listing"""
    if request.method == "POST":
        company = Company.query.filter_by(user_id=current_user.id).first()
        
        # Validate required fields
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        location = request.form.get("location", "").strip()
        
        if not all([title, description, location]):
            flash("Title, description, and location are required.", "error")
            return render_template("post_job.html")
        
        try:
            job = Job(
                employer_id=current_user.id,
                company_id=company.id if company else None,
                title=title,
                description=description,
                location=location,
                job_type=request.form.get("job_type", "full-time"),
                work_setup=request.form.get("work_setup", "on-site"),
                experience_level=request.form.get("experience_level", "mid"),
                salary_min=int(request.form.get("salary_min") or 0),
                salary_max=int(request.form.get("salary_max") or 0),
                currency=request.form.get("currency", "PHP"),
                skills_required=request.form.get("skills_required", ""),
                industry=request.form.get("industry", ""),
                is_featured=bool(request.form.get("is_featured")),
                is_urgent=bool(request.form.get("is_urgent")),
            )
            db.session.add(job)
            db.session.commit()
            flash("Job posted successfully!", "success")
            return redirect(url_for("employer.dashboard"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while posting the job.", "error")
            return render_template("post_job.html")
    
    return render_template("post_job.html")


@employer_bp.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
@employer_required
def edit_job(job_id):
    """Edit a job listing"""
    job = Job.query.get_or_404(job_id)
    
    # Check if current user owns this job
    if job.employer_id != current_user.id:
        abort(403)
    
    if request.method == "POST":
        # Validate required fields
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        location = request.form.get("location", "").strip()
        
        if not all([title, description, location]):
            flash("Title, description, and location are required.", "error")
            return render_template("edit_job.html", job=job)
        
        try:
            job.title = title
            job.description = description
            job.location = location
            job.job_type = request.form.get("job_type", "full-time")
            job.work_setup = request.form.get("work_setup", "on-site")
            job.experience_level = request.form.get("experience_level", "mid")
            job.salary_min = int(request.form.get("salary_min") or 0)
            job.salary_max = int(request.form.get("salary_max") or 0)
            job.skills_required = request.form.get("skills_required", "")
            job.industry = request.form.get("industry", "")
            job.is_featured = bool(request.form.get("is_featured"))
            job.is_urgent = bool(request.form.get("is_urgent"))
            db.session.commit()
            flash("Job updated successfully!", "success")
            return redirect(url_for("employer.dashboard"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while updating the job.", "error")
            return render_template("edit_job.html", job=job)
    
    return render_template("edit_job.html", job=job)


@employer_bp.route("/jobs/<int:job_id>/delete", methods=["POST"])
@employer_required
def delete_job(job_id):
    """Delete a job listing"""
    job = Job.query.get_or_404(job_id)
    
    # Check if current user owns this job
    if job.employer_id != current_user.id:
        abort(403)
    
    try:
        db.session.delete(job)
        db.session.commit()
        flash("Job deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the job.", "error")
    
    return redirect(url_for("employer.dashboard"))


@employer_bp.route("/jobs/<int:job_id>/toggle-status", methods=["POST"])
@employer_required
def toggle_job_status(job_id):
    """Toggle job status (active/paused)"""
    job = Job.query.get_or_404(job_id)
    
    # Check if current user owns this job
    if job.employer_id != current_user.id:
        abort(403)
    
    try:
        if job.status == "active":
            job.status = "paused"
            message = "Job paused successfully!"
        else:
            job.status = "active"
            message = "Job activated successfully!"
        
        db.session.commit()
        flash(message, "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while updating the job status.", "error")
    
    return redirect(request.referrer or url_for("employer.dashboard"))


@employer_bp.route("/applicants")
@employer_required
def applicants():
    """View all applicants for employer's jobs"""
    status_filter = request.args.get("status", "")
    job_filter = request.args.get("job_id", "", type=int)
    page = request.args.get("page", 1, type=int)
    
    # Get employer's jobs
    jobs = Job.query.filter_by(employer_id=current_user.id).all()
    job_ids = [j.id for j in jobs]
    
    # Build query
    query = Application.query.filter(Application.job_id.in_(job_ids))
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if job_filter and job_filter in job_ids:
        query = query.filter_by(job_id=job_filter)
    
    pagination = query.order_by(Application.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template(
        "applicants.html",
        applicants=pagination.items,
        pagination=pagination,
        jobs=jobs,
        status_filter=status_filter,
        job_filter=job_filter
    )


@employer_bp.route("/applicants/<int:application_id>/status", methods=["POST"])
@employer_required
def update_applicant_status(application_id):
    """Update applicant status"""
    app = Application.query.get_or_404(application_id)
    
    # Check if employer owns this job
    if app.job.employer_id != current_user.id:
        abort(403)
    
    new_status = request.form.get("status", "")
    if new_status not in ["applied", "reviewing", "interview", "offered", "rejected"]:
        flash("Invalid status.", "error")
        return redirect(request.referrer)
    
    try:
        app.status = new_status
        db.session.commit()
        flash(f"Applicant status updated to {new_status}!", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while updating status.", "error")
    
    return redirect(request.referrer or url_for("employer.applicants"))
