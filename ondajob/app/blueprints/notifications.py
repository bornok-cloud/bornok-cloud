from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Notification

notifications_bp = Blueprint("notifications", __name__, template_folder="../../templates")


@notifications_bp.route("/")
@login_required
def list_notifications():
    """View all notifications"""
    status_filter = request.args.get("status", "")
    page = request.args.get("page", 1, type=int)
    
    query = Notification.query.filter_by(user_id=current_user.id)
    
    # Filter by read status
    if status_filter == "read":
        query = query.filter_by(is_read=True)
    elif status_filter == "unread":
        query = query.filter_by(is_read=False)
    
    pagination = query.order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get unread count
    unread_count = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).count()
    
    return render_template(
        "notifications.html",
        notifications=pagination.items,
        pagination=pagination,
        status_filter=status_filter,
        unread_count=unread_count
    )


@notifications_bp.route("/unread-count")
@login_required
def unread_count():
    """Get unread notification count (API endpoint)"""
    count = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).count()
    
    return jsonify({"unread_count": count})


@notifications_bp.route("/<int:notification_id>/read", methods=["POST"])
@login_required
def mark_as_read(notification_id):
    """Mark notification as read"""
    notification = Notification.query.get_or_404(notification_id)
    
    # Check ownership
    if notification.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    
    try:
        notification.is_read = True
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@notifications_bp.route("/mark-all-read", methods=["POST"])
@login_required
def mark_all_as_read():
    """Mark all notifications as read"""
    try:
        Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).update({"is_read": True})
        db.session.commit()
        flash("All notifications marked as read.", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while marking notifications as read.", "error")
    
    return redirect(request.referrer or url_for("notifications.list_notifications"))


@notifications_bp.route("/<int:notification_id>/delete", methods=["POST"])
@login_required
def delete_notification(notification_id):
    """Delete a notification"""
    notification = Notification.query.get_or_404(notification_id)
    
    # Check ownership
    if notification.user_id != current_user.id:
        flash("Unauthorized action.", "error")
        return redirect(url_for("notifications.list_notifications"))
    
    try:
        db.session.delete(notification)
        db.session.commit()
        flash("Notification deleted.", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the notification.", "error")
    
    return redirect(request.referrer or url_for("notifications.list_notifications"))


@notifications_bp.route("/delete-all", methods=["POST"])
@login_required
def delete_all_notifications():
    """Delete all notifications"""
    try:
        Notification.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        flash("All notifications deleted.", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting notifications.", "error")
    
    return redirect(request.referrer or url_for("notifications.list_notifications"))


@notifications_bp.route("/recent")
@login_required
def recent_notifications():
    """Get recent notifications (for sidebar/header display)"""
    notifications = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).order_by(Notification.created_at.desc()).limit(5).all()
    
    return render_template(
        "notifications_dropdown.html",
        notifications=notifications
    )
