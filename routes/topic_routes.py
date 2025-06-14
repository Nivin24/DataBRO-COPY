from flask import Blueprint, render_template, session, redirect, url_for, request
from models import Topic
from extensions import db 

topic_bp = Blueprint('topic', __name__)

@topic_bp.route('/topic/<slug>')
def topic_page(slug):
    user = session.get('user')
    if not user:
        return redirect(url_for('login', next=request.path))

    topic = db.session.execute(
        db.select(Topic).filter_by(slug=slug)
    ).scalar_one_or_none()

    if topic:
        try:
            return render_template(f"{topic.name}.html", topic_name=topic.name)
        except:
            return render_template('404.html'), 404
    return render_template('404.html'), 404