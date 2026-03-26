from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app.extensions import db
from app.models import User, Profile, Company

auth_bp = Blueprint("auth", __name__, template_folder="templates")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user.role)

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash("Welcome back!", "success")
            return _redirect_by_role(user.role)
        flash("Invalid email or password.", "error")
    return render_template("login.html")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "jobseeker")

        # Check if email exists
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return render_template("signup.html")

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            role=role,
            avatar_initials=f"{first_name[:1]}{last_name[:1]}".upper(),
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        # Create profile for jobseekers or company for employers
        if role == "jobseeker":
            profile = Profile(user_id=user.id)
            db.session.add(profile)
        elif role == "employer":
            company = Company(
                user_id=user.id,
                name=f"{first_name} {last_name}'s Company",
            )
            db.session.add(company)

        db.session.commit()
        login_user(user)
        flash("Account created successfully!", "success")
        return _redirect_by_role(user.role)

    return render_template("signup.html")


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


def _redirect_by_role(role):
    if role == "employer":
        return redirect(url_for("employer.dashboard"))
    elif role == "admin":
        return redirect(url_for("admin.dashboard"))
    return redirect(url_for("jobseeker.dashboard"))
