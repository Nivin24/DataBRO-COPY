# routes/dashboard.py
from flask import session, render_template, url_for, redirect
from . import main_bp
from models import db, User
from flask import current_app as app
from flask import Blueprint, session, g

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    user_email = session.get('email')
    is_admin = False

    if user_email:
        user = db.session.execute(
            db.select(User).filter_by(email=user_email)
        ).scalar_one_or_none()

        admin_emails = ['homepcni03@gmail.com', 'databro.connect@gmail.com']
        if user and user.email.strip().lower() in [email.lower() for email in admin_emails]:
            is_admin = True

    return render_template("dashboard.html", is_admin=is_admin)


@dashboard_bp.app_context_processor
def inject_user_info():
    user_email = session.get('email')
    user = None
    is_admin = False

    if user_email:
        user = User.query.filter_by(email=user_email).first()
        if user:
            is_admin = user.email.strip().lower() in [
                'homepcni03@gmail.com',
                'databro.connect@gmail.com'
            ]

    return dict(user=user, is_admin=is_admin)