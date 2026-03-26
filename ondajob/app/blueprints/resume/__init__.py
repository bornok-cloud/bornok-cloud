from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Profile, Experience, Education

resume_bp = Blueprint("resume", __name__, template_folder="templates")


@resume_bp.route("/builder")
@login_required
def builder():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()
    experiences = Experience.query.filter_by(profile_id=profile.id).all()
    educations = Education.query.filter_by(profile_id=profile.id).all()
    return render_template(
        "resume_builder.html",
        user=current_user,
        profile=profile,
        experiences=experiences,
        educations=educations,
    )


@resume_bp.route("/save", methods=["POST"])
@login_required
def save():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.session.add(profile)

    profile.title = request.form.get("title", "")
    profile.summary = request.form.get("summary", "")
    profile.location = request.form.get("location", "")
    profile.linkedin_url = request.form.get("linkedin_url", "")
    profile.skills = request.form.get("skills", "")

    # Update user info
    current_user.first_name = request.form.get("first_name", current_user.first_name)
    current_user.last_name = request.form.get("last_name", current_user.last_name)
    current_user.phone = request.form.get("phone", current_user.phone)

    db.session.commit()
    flash("Resume saved!", "success")
    return redirect(url_for("resume.builder"))


@resume_bp.route("/add-experience", methods=["POST"])
@login_required
def add_experience():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    exp = Experience(
        profile_id=profile.id,
        job_title=request.form.get("job_title", ""),
        company=request.form.get("company", ""),
        start_date=request.form.get("start_date", ""),
        end_date=request.form.get("end_date", "Present"),
        description=request.form.get("description", ""),
    )
    db.session.add(exp)
    db.session.commit()
    flash("Experience added!", "success")
    return redirect(url_for("resume.builder"))


@resume_bp.route("/add-education", methods=["POST"])
@login_required
def add_education():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    edu = Education(
        profile_id=profile.id,
        degree=request.form.get("degree", ""),
        school=request.form.get("school", ""),
        start_year=request.form.get("start_year", ""),
        end_year=request.form.get("end_year", ""),
    )
    db.session.add(edu)
    db.session.commit()
    flash("Education added!", "success")
    return redirect(url_for("resume.builder"))
