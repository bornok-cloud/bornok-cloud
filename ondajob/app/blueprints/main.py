from flask import Blueprint, render_template
from app.extensions import db
from app.models import Job, User, Company
from sqlalchemy import func

main_bp = Blueprint("main", __name__, template_folder="../../templates")

@main_bp.route("/")
def index():
    """Landing page with real database statistics"""
    # Get real statistics from database
    total_jobs = Job.query.filter_by(status="active").count()
    total_companies = Company.query.count()
    total_jobseekers = User.query.filter_by(role="jobseeker").count()
    
    # Get job statistics by industry
    industry_stats = db.session.query(
        Job.industry,
        func.count(Job.id).label('count')
    ).filter(Job.status == "active", Job.industry.isnot(None)).group_by(Job.industry).all()
    
    # Convert to dictionary for template
    industries_data = {industry: count for industry, count in industry_stats}
    
    # Get featured jobs (limited to 6 for display)
    featured_jobs = Job.query.filter_by(
        status="active",
        is_featured=True
    ).order_by(Job.created_at.desc()).limit(6).all()
    
    # Get recent jobs if not enough featured jobs
    if len(featured_jobs) < 6:
        additional_needed = 6 - len(featured_jobs)
        recent_jobs = Job.query.filter_by(status="active").filter(
            Job.id.notin_([j.id for j in featured_jobs])
        ).order_by(Job.created_at.desc()).limit(additional_needed).all()
        featured_jobs.extend(recent_jobs)
    
    return render_template(
        "index.html",
        total_jobs=total_jobs,
        total_companies=total_companies,
        total_jobseekers=total_jobseekers,
        industries_data=industries_data,
        featured_jobs=featured_jobs,
        jobs_count_this_month=total_jobs  # Simplified for now
    )
