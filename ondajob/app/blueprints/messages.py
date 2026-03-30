from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Message, User, Notification
from datetime import datetime

messages_bp = Blueprint("messages", __name__, template_folder="../../templates")


@messages_bp.route("/")
@login_required
def inbox():
    """View inbox with all conversations"""
    page = request.args.get("page", 1, type=int)
    
    # Get distinct conversations
    sent = db.session.query(Message.receiver_id).filter_by(sender_id=current_user.id)
    received = db.session.query(Message.sender_id).filter_by(receiver_id=current_user.id)
    contact_ids = set([r[0] for r in sent.all()] + [r[0] for r in received.all()])
    
    conversations = []
    for cid in contact_ids:
        contact = User.query.get(cid)
        if not contact:
            continue
            
        last_msg = Message.query.filter(
            db.or_(
                db.and_(Message.sender_id == current_user.id, Message.receiver_id == cid),
                db.and_(Message.sender_id == cid, Message.receiver_id == current_user.id),
            )
        ).order_by(Message.created_at.desc()).first()
        
        unread = Message.query.filter_by(
            sender_id=cid, receiver_id=current_user.id, is_read=False
        ).count()
        
        conversations.append({
            "contact": contact,
            "last_message": last_msg,
            "unread": unread,
        })
    
    # Sort by last message date
    conversations.sort(
        key=lambda c: c["last_message"].created_at if c["last_message"] else datetime.utcnow(),
        reverse=True
    )
    
    # Get total unread count
    total_unread = Message.query.filter_by(
        receiver_id=current_user.id,
        is_read=False
    ).count()
    
    return render_template(
        "messages.html",
        user=current_user,
        conversations=conversations,
        total_unread=total_unread
    )


@messages_bp.route("/conversation/<int:user_id>", methods=["GET", "POST"])
@login_required
def conversation(user_id):
    """View conversation with a specific user"""
    contact = User.query.get_or_404(user_id)
    
    # Check if user is active
    if not contact.is_active:
        flash("This user account is no longer active.", "error")
        return redirect(url_for("messages.inbox"))
    
    if request.method == "POST":
        content = request.form.get("content", "").strip()
        
        if not content:
            flash("Message cannot be empty.", "error")
        else:
            try:
                msg = Message(
                    sender_id=current_user.id,
                    receiver_id=user_id,
                    content=content,
                )
                
                # Create notification for recipient
                notification = Notification(
                    user_id=user_id,
                    title="New Message",
                    message=f"You have a new message from {current_user.full_name}",
                    notification_type="message"
                )
                
                db.session.add(msg)
                db.session.add(notification)
                db.session.commit()
                flash("Message sent!", "success")
            except Exception as e:
                db.session.rollback()
                flash("An error occurred while sending the message.", "error")
        
        return redirect(url_for("messages.conversation", user_id=user_id))
    
    # Get conversation messages
    messages = Message.query.filter(
        db.or_(
            db.and_(Message.sender_id == current_user.id, Message.receiver_id == user_id),
            db.and_(Message.sender_id == user_id, Message.receiver_id == current_user.id),
        )
    ).order_by(Message.created_at.asc()).all()
    
    # Mark received messages as read
    try:
        Message.query.filter_by(
            sender_id=user_id,
            receiver_id=current_user.id,
            is_read=False
        ).update({"is_read": True})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    
    return render_template(
        "conversation.html",
        contact=contact,
        messages=messages
    )


@messages_bp.route("/send", methods=["POST"])
@login_required
def send():
    """Send a message (legacy endpoint)"""
    receiver_id = request.form.get("receiver_id", type=int)
    content = request.form.get("content", "").strip()
    
    if not receiver_id or not content:
        flash("Invalid message or recipient.", "error")
        return redirect(url_for("messages.inbox"))
    
    receiver = User.query.get_or_404(receiver_id)
    
    try:
        msg = Message(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            content=content,
        )
        
        # Create notification
        notification = Notification(
            user_id=receiver_id,
            title="New Message",
            message=f"You have a new message from {current_user.full_name}",
            notification_type="message"
        )
        
        db.session.add(msg)
        db.session.add(notification)
        db.session.commit()
        flash("Message sent!", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while sending the message.", "error")
    
    return redirect(url_for("messages.conversation", user_id=receiver_id))


@messages_bp.route("/messages/<int:message_id>/delete", methods=["POST"])
@login_required
def delete_message(message_id):
    """Delete a message"""
    message = Message.query.get_or_404(message_id)
    
    # Check if user is the sender
    if message.sender_id != current_user.id:
        abort(403)
    
    receiver_id = message.receiver_id
    
    try:
        db.session.delete(message)
        db.session.commit()
        flash("Message deleted.", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the message.", "error")
    
    return redirect(url_for("messages.conversation", user_id=receiver_id))


@messages_bp.route("/mark-as-read/<int:message_id>", methods=["POST"])
@login_required
def mark_as_read(message_id):
    """Mark a message as read"""
    message = Message.query.get_or_404(message_id)
    
    # Check if user is the receiver
    if message.receiver_id != current_user.id:
        abort(403)
    
    try:
        message.is_read = True
        db.session.commit()
        return {"success": True}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500
