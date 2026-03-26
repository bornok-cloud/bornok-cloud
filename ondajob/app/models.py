from datetime import datetime
from app.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


# ── User ─────────────────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("jobseeker", "employer", "admin"), default="jobseeker", nullable=False)
    avatar_initials = db.Column(db.String(5))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile = db.relationship("Profile", backref="user", uselist=False, cascade="all, delete-orphan")
    jobs_posted = db.relationship("Job", backref="employer", lazy="dynamic", foreign_keys="Job.employer_id")
    applications = db.relationship("Application", backref="applicant", lazy="dynamic", foreign_keys="Application.user_id")
    sent_messages = db.relationship("Message", backref="sender", lazy="dynamic", foreign_keys="Message.sender_id")
    received_messages = db.relationship("Message", backref="receiver", lazy="dynamic", foreign_keys="Message.receiver_id")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<User {self.email}>"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ── Profile (Job Seeker details) ─────────────────────────────
class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    title = db.Column(db.String(200))  # e.g. "Senior Frontend Developer"
    summary = db.Column(db.Text)
    location = db.Column(db.String(200))
    linkedin_url = db.Column(db.String(500))
    portfolio_url = db.Column(db.String(500))
    resume_score = db.Column(db.Integer, default=0)
    skills = db.Column(db.Text)  # comma-separated
    experience_years = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    experiences = db.relationship("Experience", backref="profile", lazy="dynamic", cascade="all, delete-orphan")
    educations = db.relationship("Education", backref="profile", lazy="dynamic", cascade="all, delete-orphan")


# ── Experience ───────────────────────────────────────────────
class Experience(db.Model):
    __tablename__ = "experiences"

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("profiles.id"), nullable=False)
    job_title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50), default="Present")
    description = db.Column(db.Text)


# ── Education ────────────────────────────────────────────────
class Education(db.Model):
    __tablename__ = "educations"

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("profiles.id"), nullable=False)
    degree = db.Column(db.String(200), nullable=False)
    school = db.Column(db.String(200), nullable=False)
    start_year = db.Column(db.String(10))
    end_year = db.Column(db.String(10))


# ── Company (Employer profile) ───────────────────────────────
class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    industry = db.Column(db.String(100))
    location = db.Column(db.String(200))
    website = db.Column(db.String(500))
    employee_count = db.Column(db.String(50))
    logo_emoji = db.Column(db.String(10), default="🏢")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("company", uselist=False))
    jobs = db.relationship("Job", backref="company", lazy="dynamic")


# ── Job ──────────────────────────────────────────────────────
class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    job_type = db.Column(db.Enum("full-time", "part-time", "contract", "freelance", "internship"), default="full-time")
    work_setup = db.Column(db.Enum("remote", "on-site", "hybrid"), default="on-site")
    experience_level = db.Column(db.Enum("entry", "mid", "senior", "lead", "manager", "director"), default="mid")
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    currency = db.Column(db.String(5), default="PHP")
    skills_required = db.Column(db.Text)  # comma-separated
    industry = db.Column(db.String(100))
    is_featured = db.Column(db.Boolean, default=False)
    is_urgent = db.Column(db.Boolean, default=False)
    status = db.Column(db.Enum("active", "paused", "closed"), default="active")
    views_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    applications = db.relationship("Application", backref="job", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def salary_display(self):
        if self.salary_min and self.salary_max:
            return f"₱{self.salary_min // 1000}K–{self.salary_max // 1000}K"
        return "Negotiable"

    @property
    def time_ago(self):
        diff = datetime.utcnow() - self.created_at
        if diff.days == 0:
            return "Today"
        elif diff.days == 1:
            return "1 day ago"
        else:
            return f"{diff.days} days ago"


# ── Application ──────────────────────────────────────────────
class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    status = db.Column(db.Enum("applied", "reviewing", "interview", "offered", "rejected"), default="applied")
    cover_letter = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ── Saved Jobs ───────────────────────────────────────────────
class SavedJob(db.Model):
    __tablename__ = "saved_jobs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="saved_jobs")
    job = db.relationship("Job", backref="saves")


# ── Message ──────────────────────────────────────────────────
class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ── Notification ─────────────────────────────────────────────
class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200))
    message = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    notification_type = db.Column(db.String(50))  # application, interview, message, system
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="notifications")


# ── Report (for admin) ──────────────────────────────────────
class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    reason = db.Column(db.Enum("spam", "misleading", "scam", "inappropriate", "other"), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.Enum("pending", "reviewed", "resolved"), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reporter = db.relationship("User", foreign_keys=[reporter_id], backref="reports_filed")
    reported_job = db.relationship("Job", backref="reports")
