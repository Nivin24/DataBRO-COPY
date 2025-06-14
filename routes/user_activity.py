# routes/user_activity.py

from flask import Blueprint, session
from models import db, User, UserActivity
from datetime import datetime, timezone

user_activity_bp = Blueprint('user_activity', __name__)

@user_activity_bp.before_app_request
def log_daily_activity():
    user = session.get('user')
    if user:
        user_id = user['id']
        today_utc = datetime.now(timezone.utc).date()
        existing = UserActivity.query.filter_by(user_id=user_id, activity_date=today_utc).first()

        if not existing:
            new_activity = UserActivity(user_id=user_id, activity_date=today_utc)
            db.session.add(new_activity)
            db.session.commit()