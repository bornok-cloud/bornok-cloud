from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Job, Application, SavedJob

jobs_bp = Blueprint("jobs", __name__, template_folder="../../templates")


@jobs_bp.route("/search")
def search():
    """Advanced job search with filtering"""
    query = request.args.get("q", "")
    location = request.args.get("location", "")
    job_type = request.args.get("job_type", "")
    work_setup = request.args.get("work_setup", "")
    experience_level = request.args.get("experience_level", "")
    industry = request.args.get("industry", "")
    salary_min = request.args.get("salary_min", "", type=int)
    salary_max = request.args.get("salary_max", "", type=int)
    sort_by = request.args.get("sort", "relevant")
    page = request.args.get("page", 1, type=int)

    jobs_query = Job.query.filter_by(status="active")

    # Text search across title, description, and skills
    if query:
        jobs_query = jobs_query.filter(
            db.or_(
                Job.title.ilike(f"%{query}%"),
                Job.description.ilike(f"%{query}%"),
                Job.skills_required.ilike(f"%{query}%"),
            )
        )

    # Filter by location
    if location:
        jobs_query = jobs_query.filter(Job.location.ilike(f"%{location}%"))

    # Filter by job type (full-time, part-time, etc.)
    if job_type:
        jobs_query = jobs_query.filter_by(job_type=job_type)

    # Filter by work setup (remote, on-site, hybrid)
    if work_setup:
        jobs_query = jobs_query.filter_by(work_setup=work_setup)

    # Filter by experience level (entry, mid, senior, etc.)
    if experience_level:
        jobs_query = jobs_query.filter_by(experience_level=experience_level)

    # Filter by industry
    if industry:
        jobs_query = jobs_query.filter_by(industry=industry)

    # Filter by salary range
    if salary_min:
        jobs_query = jobs_query.filter(Job.salary_min >= salary_min)
    if salary_max:
        jobs_query = jobs_query.filter(Job.salary_max <= salary_max)

    # Sorting options
    if sort_by == "newest":
        jobs_query = jobs_query.order_by(Job.created_at.desc())
    elif sort_by == "salary":
        jobs_query = jobs_query.order_by(Job.salary_max.desc())
    elif sort_by == "featured":
        jobs_query = jobs_query.order_by(Job.is_featured.desc(), Job.created_at.desc())
    elif sort_by == "views":
        jobs_query = jobs_query.order_by(Job.views_count.desc())
    else:  # "relevant"
        jobs_query = jobs_query.order_by(Job.is_featured.desc(), Job.is_urgent.desc(), Job.created_at.desc())

    pagination = jobs_query.paginate(page=page, per_page=10, error_out=False)
    total_count = jobs_query.count()

    # Get available filter options
    industries = db.session.query(Job.industry).filter(Job.industry.isnot(None)).distinct().all()
    industries = [ind[0] for ind in industries if ind[0]]

    return render_template(
        "search_jobs.html",
        jobs=pagination.items,
        pagination=pagination,
        total_count=total_count,
        query=query,
        location=location,
        job_type=job_type,
        work_setup=work_setup,
        experience_level=experience_level,
        industry=industry,
        salary_min=salary_min,
        salary_max=salary_max,
        sort_by=sort_by,
        industries=industries
    )


@jobs_bp.route("/<int:job_id>")
def job_details(job_id):
    """View job details"""
    job = Job.query.get_or_404(job_id)
    
    # Increment views count
    job.views_count = (job.views_count or 0) + 1
    db.session.commit()
    
    # Check if current user has applied or saved this job
    has_applied = False
    has_saved = False
    if current_user.is_authenticated:
        has_applied = Application.query.filter_by(
            user_id=current_user.id, job_id=job_id
        ).first() is not None
        has_saved = SavedJob.query.filter_by(
            user_id=current_user.id, job_id=job_id
        ).first() is not None
    
    return render_template(
        "job_details.html",
        job=job,
        has_applied=has_applied,
        has_saved=has_saved
    )


@jobs_bp.route("/apply/<int:job_id>", methods=["POST"])
@login_required
def apply(job_id):
    """Apply for a job"""
    job = Job.query.get_or_404(job_id)
    
    # Check if user is a jobseeker
    if current_user.role != "jobseeker":
        flash("Only job seekers can apply for positions.", "error")
        return redirect(url_for("jobs.job_details", job_id=job_id))
    
    # Check if already applied
    existing = Application.query.filter_by(user_id=current_user.id, job_id=job_id).first()
    if existing:
        flash("You already applied for this job.", "info")
    else:
        app = Application(
            user_id=current_user.id,
            job_id=job_id,
            cover_letter=request.form.get("cover_letter", ""),
        )
        db.session.add(app)
        db.session.commit()
        flash(f"Applied to {job.title} successfully!", "success")
    
    return redirect(url_for("jobs.job_details", job_id=job_id))


@jobs_bp.route("/save/<int:job_id>", methods=["POST"])
@login_required
def save_job(job_id):
    """Save/unsave a job"""
    job = Job.query.get_or_404(job_id)
    
    existing = SavedJob.query.filter_by(user_id=current_user.id, job_id=job_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash("Job removed from saved.", "info")
    else:
        saved = SavedJob(user_id=current_user.id, job_id=job_id)
        db.session.add(saved)
        db.session.commit()
        flash("Job saved!", "success")
    
    return redirect(request.referrer or url_for("jobs.search"))
