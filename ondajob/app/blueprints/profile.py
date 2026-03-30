from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User, Profile, Experience, Education
from app.blueprints.auth import jobseeker_required
from datetime import datetime

profile_bp = Blueprint("profile", __name__, template_folder="../../templates")


@profile_bp.route("/")
@jobseeker_required
def view_profile():
    """View own profile"""
    profile = current_user.profile
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()
    
    # Calculate resume score
    resume_score = calculate_resume_score(profile)
    
    return render_template(
        "profile.html",
        profile=profile,
        user=current_user,
        resume_score=resume_score
    )


@profile_bp.route("/public/<int:user_id>")
def public_profile(user_id):
    """View public profile (for employers)"""
    user = User.query.get_or_404(user_id)
    
    # Only allow viewing jobseeker profiles
    if user.role != "jobseeker":
        abort(404)
    
    # Check if user is active
    if not user.is_active:
        abort(404)
    
    profile = user.profile
    if not profile:
        abort(404)
    
    resume_score = calculate_resume_score(profile)
    
    return render_template(
        "public_profile.html",
        profile=profile,
        user=user,
        resume_score=resume_score
    )


@profile_bp.route("/edit", methods=["GET", "POST"])
@jobseeker_required
def edit_profile():
    """Edit own profile"""
    profile = current_user.profile
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()
    
    if request.method == "POST":
        try:
            # Update user basic info
            current_user.first_name = request.form.get("first_name", "").strip()
            current_user.last_name = request.form.get("last_name", "").strip()
            current_user.phone = request.form.get("phone", "").strip()
            
            # Update profile info
            profile.title = request.form.get("title", "").strip()
            profile.summary = request.form.get("summary", "").strip()
            profile.location = request.form.get("location", "").strip()
            profile.linkedin_url = request.form.get("linkedin_url", "").strip()
            profile.portfolio_url = request.form.get("portfolio_url", "").strip()
            profile.skills = request.form.get("skills", "").strip()
            
            # Parse experience years
            try:
                profile.experience_years = int(request.form.get("experience_years", 0) or 0)
            except (ValueError, TypeError):
                profile.experience_years = 0
            
            db.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for("profile.view_profile"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while updating your profile.", "error")
    
    resume_score = calculate_resume_score(profile)
    
    return render_template(
        "profile_edit.html",
        profile=profile,
        user=current_user,
        resume_score=resume_score
    )


@profile_bp.route("/experiences")
@jobseeker_required
def view_experiences():
    """View all experiences"""
    profile = current_user.profile
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()
    
    experiences = profile.experiences.order_by(Experience.id.desc()).all()
    
    return render_template(
        "experiences.html",
        experiences=experiences,
        profile=profile
    )


@profile_bp.route("/experiences/add", methods=["GET", "POST"])
@jobseeker_required
def add_experience():
    """Add a new experience"""
    profile = current_user.profile
    if not profile:
        abort(404)
    
    if request.method == "POST":
        try:
            job_title = request.form.get("job_title", "").strip()
            company = request.form.get("company", "").strip()
            
            if not all([job_title, company]):
                flash("Job title and company are required.", "error")
                return render_template("add_experience.html")
            
            experience = Experience(
                profile_id=profile.id,
                job_title=job_title,
                company=company,
                start_date=request.form.get("start_date", "").strip(),
                end_date=request.form.get("end_date", "Present"),
                description=request.form.get("description", "").strip()
            )
            
            db.session.add(experience)
            db.session.commit()
            flash("Experience added successfully!", "success")
            return redirect(url_for("profile.view_experiences"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while adding experience.", "error")
    
    return render_template("add_experience.html")


@profile_bp.route("/experiences/<int:experience_id>/edit", methods=["GET", "POST"])
@jobseeker_required
def edit_experience(experience_id):
    """Edit an experience"""
    experience = Experience.query.get_or_404(experience_id)
    
    # Check if experience belongs to current user
    if experience.profile.user_id != current_user.id:
        abort(403)
    
    if request.method == "POST":
        try:
            job_title = request.form.get("job_title", "").strip()
            company = request.form.get("company", "").strip()
            
            if not all([job_title, company]):
                flash("Job title and company are required.", "error")
                return render_template("edit_experience.html", experience=experience)
            
            experience.job_title = job_title
            experience.company = company
            experience.start_date = request.form.get("start_date", "").strip()
            experience.end_date = request.form.get("end_date", "Present")
            experience.description = request.form.get("description", "").strip()
            
            db.session.commit()
            flash("Experience updated successfully!", "success")
            return redirect(url_for("profile.view_experiences"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while updating experience.", "error")
    
    return render_template("edit_experience.html", experience=experience)


@profile_bp.route("/experiences/<int:experience_id>/delete", methods=["POST"])
@jobseeker_required
def delete_experience(experience_id):
    """Delete an experience"""
    experience = Experience.query.get_or_404(experience_id)
    
    # Check if experience belongs to current user
    if experience.profile.user_id != current_user.id:
        abort(403)
    
    try:
        db.session.delete(experience)
        db.session.commit()
        flash("Experience deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting experience.", "error")
    
    return redirect(url_for("profile.view_experiences"))


@profile_bp.route("/educations")
@jobseeker_required
def view_educations():
    """View all educations"""
    profile = current_user.profile
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()
    
    educations = profile.educations.order_by(Education.id.desc()).all()
    
    return render_template(
        "educations.html",
        educations=educations,
        profile=profile
    )


@profile_bp.route("/educations/add", methods=["GET", "POST"])
@jobseeker_required
def add_education():
    """Add a new education"""
    profile = current_user.profile
    if not profile:
        abort(404)
    
    if request.method == "POST":
        try:
            degree = request.form.get("degree", "").strip()
            school = request.form.get("school", "").strip()
            
            if not all([degree, school]):
                flash("Degree and school are required.", "error")
                return render_template("add_education.html")
            
            education = Education(
                profile_id=profile.id,
                degree=degree,
                school=school,
                start_year=request.form.get("start_year", "").strip(),
                end_year=request.form.get("end_year", "").strip()
            )
            
            db.session.add(education)
            db.session.commit()
            flash("Education added successfully!", "success")
            return redirect(url_for("profile.view_educations"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while adding education.", "error")
    
    return render_template("add_education.html")


@profile_bp.route("/educations/<int:education_id>/edit", methods=["GET", "POST"])
@jobseeker_required
def edit_education(education_id):
    """Edit an education"""
    education = Education.query.get_or_404(education_id)
    
    # Check if education belongs to current user
    if education.profile.user_id != current_user.id:
        abort(403)
    
    if request.method == "POST":
        try:
            degree = request.form.get("degree", "").strip()
            school = request.form.get("school", "").strip()
            
            if not all([degree, school]):
                flash("Degree and school are required.", "error")
                return render_template("edit_education.html", education=education)
            
            education.degree = degree
            education.school = school
            education.start_year = request.form.get("start_year", "").strip()
            education.end_year = request.form.get("end_year", "").strip()
            
            db.session.commit()
            flash("Education updated successfully!", "success")
            return redirect(url_for("profile.view_educations"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while updating education.", "error")
    
    return render_template("edit_education.html", education=education)


@profile_bp.route("/educations/<int:education_id>/delete", methods=["POST"])
@jobseeker_required
def delete_education(education_id):
    """Delete an education"""
    education = Education.query.get_or_404(education_id)
    
    # Check if education belongs to current user
    if education.profile.user_id != current_user.id:
        abort(403)
    
    try:
        db.session.delete(education)
        db.session.commit()
        flash("Education deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting education.", "error")
    
    return redirect(url_for("profile.view_educations"))


def calculate_resume_score(profile):
    """Calculate resume completion score"""
    score = 0
    
    # Basic profile info (30 points)
    if profile.user and profile.user.first_name:
        score += 5
    if profile.user and profile.user.last_name:
        score += 5
    if profile.user and profile.user.phone:
        score += 5
    if profile.title:
        score += 5
    if profile.summary and len(profile.summary) > 20:
        score += 5
    if profile.location:
        score += 5
    
    # Experience (35 points)
    experiences = profile.experiences.all()
    if experiences:
        score += min(20, len(experiences) * 5)  # Max 20 points
    if profile.skills and len(profile.skills.split(",")) >= 3:
        score += 15
    
    # Education (35 points)
    educations = profile.educations.all()
    if educations:
        score += min(20, len(educations) * 10)  # Max 20 points
    if profile.linkedin_url:
        score += 8
    if profile.portfolio_url:
        score += 7
    
    return min(100, score)
