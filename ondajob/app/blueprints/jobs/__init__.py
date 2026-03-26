from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Job, Application, SavedJob

jobs_bp = Blueprint("jobs", __name__, template_folder="templates")


@jobs_bp.route("/search")
def search():
    query = request.args.get("q", "")
    location = request.args.get("location", "")
    job_type = request.args.get("job_type", "")
    work_setup = request.args.get("work_setup", "")
    sort_by = request.args.get("sort", "relevant")
    page = request.args.get("page", 1, type=int)

    jobs_query = Job.query.filter_by(status="active")

    if query:
        jobs_query = jobs_query.filter(
            db.or_(
                Job.title.ilike(f"%{query}%"),
                Job.description.ilike(f"%{query}%"),
                Job.skills_required.ilike(f"%{query}%"),
            )
        )
    if location:
        jobs_query = jobs_query.filter(Job.location.ilike(f"%{location}%"))
    if job_type:
        jobs_query = jobs_query.filter_by(job_type=job_type)
    if work_setup:
        jobs_query = jobs_query.filter_by(work_setup=work_setup)

    if sort_by == "newest":
        jobs_query = jobs_query.order_by(Job.created_at.desc())
    elif sort_by == "salary":
        jobs_query = jobs_query.order_by(Job.salary_max.desc())
    else:
        jobs_query = jobs_query.order_by(Job.is_featured.desc(), Job.created_at.desc())

    pagination = jobs_query.paginate(page=page, per_page=10, error_out=False)
    total_count = jobs_query.count()

    return render_template(
        "search_jobs.html",
        jobs=pagination.items,
        pagination=pagination,
        total_count=total_count,
        query=query,
        location=location,
    )


@jobs_bp.route("/apply/<int:job_id>", methods=["POST"])
@login_required
def apply(job_id):
    job = Job.query.get_or_404(job_id)
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
    return redirect(url_for("jobseeker.dashboard"))


@jobs_bp.route("/save/<int:job_id>", methods=["POST"])
@login_required
def save_job(job_id):
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
