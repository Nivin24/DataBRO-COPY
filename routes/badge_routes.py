# routes/badge_routes.py

from flask import Blueprint, session, g
from models import db, User
from utils import get_user_badges

badge_bp = Blueprint('badge', __name__)

@badge_bp.before_app_request
def assign_badges_if_logged_in():
    user = session.get('user')
    if user:
        user_id = user['id']
        badges = get_user_badges(user_id)
        user['badges'] = badges
        session['user'] = user

        db_user = db.session.get(User, user_id)
        if db_user and db_user.badges != badges:
            db_user.badges = badges
            db.session.commit()