from flask import Flask
from config import config
from app.extensions import db, migrate, login_manager


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # ── Initialize extensions ────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # ── Import models so they are registered ─────────────────
    from app import models  # noqa: F401

    # ── Register Blueprints ──────────────────────────────────
    from app.blueprints.main import main_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.jobseeker import jobseeker_bp
    from app.blueprints.employer import employer_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.jobs import jobs_bp
    from app.blueprints.messages import messages_bp
    from app.blueprints.resume import resume_bp
    from app.blueprints.profile import profile_bp
    from app.blueprints.interviews import interviews_bp
    from app.blueprints.notifications import notifications_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(jobseeker_bp, url_prefix="/jobseeker")
    app.register_blueprint(employer_bp, url_prefix="/employer")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(jobs_bp, url_prefix="/jobs")
    app.register_blueprint(messages_bp, url_prefix="/messages")
    app.register_blueprint(resume_bp, url_prefix="/resume")
    app.register_blueprint(profile_bp, url_prefix="/profile")
    app.register_blueprint(interviews_bp, url_prefix="/interviews")
    app.register_blueprint(notifications_bp, url_prefix="/notifications")

    # ── Create tables if they don't exist ────────────────────
    with app.app_context():
        db.create_all()

    return app
