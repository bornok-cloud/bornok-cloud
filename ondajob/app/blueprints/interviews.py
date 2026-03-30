from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Interview, Application, Job, Notification
from app.blueprints.auth import employer_required, jobseeker_required
from datetime import datetime, timedelta

interviews_bp = Blueprint("interviews", __name__, template_folder="../../templates")


@interviews_bp.route("/schedule/<int:application_id>", methods=["GET", "POST"])
@employer_required
def schedule_interview(application_id):
    """Schedule an interview for an applicant"""
    app = Application.query.get_or_404(application_id)
    
    # Check if employer owns this job
    if app.job.employer_id != current_user.id:
        abort(403)
    
    if request.method == "POST":
        try:
            scheduled_date_str = request.form.get("scheduled_date", "")
            scheduled_time_str = request.form.get("scheduled_time", "")
            interview_type = request.form.get("interview_type", "")
            notes = request.form.get("notes", "").strip()
            
            # Validate inputs
            if not all([scheduled_date_str, scheduled_time_str, interview_type]):
                flash("Date, time, and interview type are required.", "error")
                return render_template("schedule_interview.html", application=app)
            
            if interview_type not in ["phone", "video", "in-person"]:
                flash("Invalid interview type.", "error")
                return render_template("schedule_interview.html", application=app)
            
            # Combine date and time
            try:
                scheduled_datetime = datetime.strptime(
                    f"{scheduled_date_str} {scheduled_time_str}",
                    "%Y-%m-%d %H:%M"
                )
            except ValueError:
                flash("Invalid date or time format.", "error")
                return render_template("schedule_interview.html", application=app)
            
            # Create interview
            interview = Interview(
                application_id=app.id,
                scheduled_date=scheduled_datetime,
                interview_type=interview_type,
                notes=notes,
                status="scheduled"
            )
            
            db.session.add(interview)
            
            # Update application status
            app.status = "interview"
            
            # Create notification for applicant
            notification = Notification(
                user_id=app.user_id,
                title="Interview Scheduled",
                message=f"Your interview for {app.job.title} has been scheduled for {scheduled_datetime.strftime('%B %d, %Y at %I:%M %p')}",
                notification_type="interview"
            )
            db.session.add(notification)
            
            db.session.commit()
            flash("Interview scheduled successfully!", "success")
            return redirect(url_for("employer.applicants"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while scheduling the interview.", "error")
    
    return render_template("schedule_interview.html", application=app)


@interviews_bp.route("/<int:interview_id>")
@login_required
def view_interview(interview_id):
    """View interview details"""
    interview = Interview.query.get_or_404(interview_id)
    app = interview.application
    
    # Check authorization (employer who scheduled or applicant)
    if current_user.id != app.job.employer_id and current_user.id != app.user_id:
        abort(403)
    
    return render_template("interview_details.html", interview=interview)


@interviews_bp.route("/<int:interview_id>/edit", methods=["GET", "POST"])
@employer_required
def edit_interview(interview_id):
    """Edit an interview"""
    interview = Interview.query.get_or_404(interview_id)
    app = interview.application
    
    # Check if employer owns this job
    if app.job.employer_id != current_user.id:
        abort(403)
    
    if request.method == "POST":
        try:
            scheduled_date_str = request.form.get("scheduled_date", "")
            scheduled_time_str = request.form.get("scheduled_time", "")
            interview_type = request.form.get("interview_type", "")
            notes = request.form.get("notes", "").strip()
            
            # Validate inputs
            if not all([scheduled_date_str, scheduled_time_str, interview_type]):
                flash("Date, time, and interview type are required.", "error")
                return render_template("edit_interview.html", interview=interview)
            
            if interview_type not in ["phone", "video", "in-person"]:
                flash("Invalid interview type.", "error")
                return render_template("edit_interview.html", interview=interview)
            
            # Combine date and time
            try:
                scheduled_datetime = datetime.strptime(
                    f"{scheduled_date_str} {scheduled_time_str}",
                    "%Y-%m-%d %H:%M"
                )
            except ValueError:
                flash("Invalid date or time format.", "error")
                return render_template("edit_interview.html", interview=interview)
            
            # Update interview
            interview.scheduled_date = scheduled_datetime
            interview.interview_type = interview_type
            interview.notes = notes
            
            db.session.commit()
            flash("Interview updated successfully!", "success")
            return redirect(url_for("interviews.view_interview", interview_id=interview.id))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while updating the interview.", "error")
    
    return render_template("edit_interview.html", interview=interview)


@interviews_bp.route("/<int:interview_id>/complete", methods=["GET", "POST"])
@employer_required
def complete_interview(interview_id):
    """Mark interview as completed with feedback"""
    interview = Interview.query.get_or_404(interview_id)
    app = interview.application
    
    # Check if employer owns this job
    if app.job.employer_id != current_user.id:
        abort(403)
    
    if request.method == "POST":
        try:
            feedback = request.form.get("feedback", "").strip()
            next_status = request.form.get("next_status", "interview")
            
            if not feedback:
                flash("Feedback is required.", "error")
                return render_template("complete_interview.html", interview=interview)
            
            if next_status not in ["interview", "offered", "rejected"]:
                flash("Invalid status.", "error")
                return render_template("complete_interview.html", interview=interview)
            
            # Update interview
            interview.feedback = feedback
            interview.status = "completed"
            
            # Update application status
            app.status = next_status
            
            # Create notification for applicant
            if next_status == "offered":
                message = f"Congratulations! You have been offered the position of {app.job.title}!"
            elif next_status == "rejected":
                message = f"Thank you for your interest in {app.job.title}. We've decided to move forward with other candidates."
            else:
                message = f"Your interview for {app.job.title} has been completed. You will hear from us soon."
            
            notification = Notification(
                user_id=app.user_id,
                title="Interview Update",
                message=message,
                notification_type="interview"
            )
            db.session.add(notification)
            
            db.session.commit()
            flash("Interview completed successfully!", "success")
            return redirect(url_for("employer.applicants"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while completing the interview.", "error")
    
    return render_template("complete_interview.html", interview=interview)


@interviews_bp.route("/<int:interview_id>/cancel", methods=["POST"])
@employer_required
def cancel_interview(interview_id):
    """Cancel an interview"""
    interview = Interview.query.get_or_404(interview_id)
    app = interview.application
    
    # Check if employer owns this job
    if app.job.employer_id != current_user.id:
        abort(403)
    
    try:
        interview.status = "cancelled"
        app.status = "applied"  # Reset to applied status
        
        # Create notification for applicant
        notification = Notification(
            user_id=app.user_id,
            title="Interview Cancelled",
            message=f"Your interview for {app.job.title} has been cancelled.",
            notification_type="interview"
        )
        db.session.add(notification)
        
        db.session.commit()
        flash("Interview cancelled successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while cancelling the interview.", "error")
    
    return redirect(request.referrer or url_for("employer.applicants"))


@interviews_bp.route("/")
@login_required
def interviews_calendar():
    """View interview calendar"""
    if current_user.role == "employer":
        # Show all interviews for employer's jobs
        interviews = db.session.query(Interview)\
            .join(Application)\
            .join(Job)\
            .filter(Job.employer_id == current_user.id)\
            .order_by(Interview.scheduled_date.desc())\
            .all()
    else:
        # Show interviews for applicant
        interviews = db.session.query(Interview)\
            .join(Application)\
            .filter(Application.user_id == current_user.id)\
            .order_by(Interview.scheduled_date.desc())\
            .all()
    
    return render_template("interviews_calendar.html", interviews=interviews)


@interviews_bp.route("/upcoming")
@login_required
def upcoming_interviews():
    """View upcoming interviews"""
    now = datetime.utcnow()
    
    if current_user.role == "employer":
        # Show upcoming interviews for employer's jobs
        interviews = db.session.query(Interview)\
            .join(Application)\
            .join(Job)\
            .filter(
                Job.employer_id == current_user.id,
                Interview.scheduled_date > now,
                Interview.status == "scheduled"
            )\
            .order_by(Interview.scheduled_date.asc())\
            .all()
    else:
        # Show upcoming interviews for applicant
        interviews = db.session.query(Interview)\
            .join(Application)\
            .filter(
                Application.user_id == current_user.id,
                Interview.scheduled_date > now,
                Interview.status == "scheduled"
            )\
            .order_by(Interview.scheduled_date.asc())\
            .all()
    
    return render_template("upcoming_interviews.html", interviews=interviews)
