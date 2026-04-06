from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Message, User
from datetime import datetime

messages_bp = Blueprint("messages", __name__, template_folder="../../templates")


@messages_bp.route("/")
@login_required
def inbox():
    # Get distinct conversations
    sent = db.session.query(Message.receiver_id).filter_by(sender_id=current_user.id)
    received = db.session.query(Message.sender_id).filter_by(receiver_id=current_user.id)
    contact_ids = set([r[0] for r in sent.all()] + [r[0] for r in received.all()])
    
    conversations = []
    for cid in contact_ids:
        contact = User.query.get(cid)
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
    
    conversations.sort(key=lambda c: c["last_message"].created_at if c["last_message"] else 0, reverse=True)
    
    return render_template("messages.html", user=current_user, conversations=conversations, now=datetime.utcnow())


@messages_bp.route("/send", methods=["POST"])
@login_required
def send():
    receiver_id = request.form.get("receiver_id", type=int)
    content = request.form.get("content", "").strip()
    if receiver_id and content:
        msg = Message(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            content=content,
        )
        db.session.add(msg)
        db.session.commit()
    return redirect(url_for("messages.inbox"))
