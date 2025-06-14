# routes/home_routes.py

from flask import Blueprint, render_template, session
from models import db, Topic

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def home():
    user = session.get('user')
    topics = db.session.execute(
        db.select(Topic).order_by(Topic.display_order)
    ).scalars().all()
    return render_template('home.html', topics=topics, user=user)

@home_bp.route('/debug-topics')
def debug_topics():
    topics = db.session.execute(db.select(Topic)).scalars().all()
    return "<br>".join([f"{t.name} - {t.slug}" for t in topics]) or "No topics found."