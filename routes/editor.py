# routes/editor.py
from flask import session, render_template, redirect, url_for
from . import main_bp
from models import db, User, Topic
from flask import current_app as app
from flask import Blueprint, session, g

editor_bp = Blueprint('editor', __name__)

@editor_bp.route('/editor')
def editor():
    user_email = session.get('email')
    is_admin = False

    if user_email:
        user = db.session.execute(
            db.select(User).filter_by(email=user_email)
        ).scalar_one_or_none()

        admin_emails = ['homepcni03@gmail.com', 'databro.connect@gmail.com']
        if user and user.email.strip().lower() in [email.lower() for email in admin_emails]:
            is_admin = True

    if not is_admin:
        return redirect(url_for('main.home'))

    topics = db.session.execute(db.select(Topic)).scalars().all()
    return render_template("admin_editor.html", is_admin=is_admin, topics=topics)