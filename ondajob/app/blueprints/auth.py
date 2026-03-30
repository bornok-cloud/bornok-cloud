from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, current_user, login_required
from app.extensions import db
from app.models import User, Profile, Company
from functools import wraps
import re

auth_bp = Blueprint("auth", __name__, template_folder="../../templates")

"""
AUTHENTICATION SECURITY POLICY:
================================
1. NO automatic user login based on database existence
2. EVERY dashboard route MUST have @login_required or role-based decorator
3. Users MUST provide credentials (email + password) to authenticate
4. Session protection enabled at LoginManager level
5. All routes check current_user.is_authenticated before granting access
6. Role-based decorators enforce permissions after authentication
"""

# ── Role-based Access Control Decorators ────────────────────
def jobseeker_required(f):
    """Decorator to require jobseeker role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in first.", "warning")
            return redirect(url_for("auth.login"))
        if current_user.role != "jobseeker" or not current_user.is_active:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def employer_required(f):
    """Decorator to require employer role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in first.", "warning")
            return redirect(url_for("auth.login"))
        if current_user.role != "employer" or not current_user.is_active:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in first.", "warning")
            return redirect(url_for("auth.login"))
        if current_user.role != "admin" or not current_user.is_active:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


# ── Validation Functions ─────────────────────────────────────
def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_phone(phone):
    """Validate phone format (Philippines)"""
    if not phone:
        return True  # Optional field
    # Accept +63, 0, or 09 formats
    pattern = r'^(\+63|0)?9\d{9}$'
    return re.match(pattern, phone.replace(" ", "").replace("-", "")) is not None


def is_strong_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit"
    return True, None


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user.role)

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        # Validate input
        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template("login.html")

        if not is_valid_email(email):
            flash("Invalid email format.", "error")
            return render_template("login.html")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            # Check if user account is active
            if not user.is_active:
                flash("Your account has been deactivated. Contact support.", "error")
                return render_template("login.html")
            
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
        password_confirm = request.form.get("password_confirm", "")
        role = request.form.get("role", "jobseeker")

        # Validate required fields
        if not all([first_name, last_name, email, password]):
            flash("All required fields must be filled.", "error")
            return render_template("signup.html")

        # Validate name length
        if len(first_name) < 2 or len(last_name) < 2:
            flash("First and last names must be at least 2 characters.", "error")
            return render_template("signup.html")

        # Validate email format
        if not is_valid_email(email):
            flash("Invalid email format.", "error")
            return render_template("signup.html")

        # Check if email exists
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return render_template("signup.html")

        # Validate phone format (if provided)
        if phone and not is_valid_phone(phone):
            flash("Invalid phone number format.", "error")
            return render_template("signup.html")

        # Validate password strength
        if password != password_confirm:
            flash("Passwords do not match.", "error")
            return render_template("signup.html")

        is_strong, error_msg = is_strong_password(password)
        if not is_strong:
            flash(error_msg, "error")
            return render_template("signup.html")

        # Validate role
        if role not in ["jobseeker", "employer"]:
            flash("Invalid role selected.", "error")
            return render_template("signup.html")

        try:
            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                role=role,
                avatar_initials=f"{first_name[:1]}{last_name[:1]}".upper(),
                is_active=True
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
        except Exception as e:
            db.session.rollback()
            flash("An error occurred during registration. Please try again.", "error")
            return render_template("signup.html")

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
