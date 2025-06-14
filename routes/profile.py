# routes/profile.py
from flask import session, redirect, url_for, render_template
from . import main_bp
from utils import get_user_badges  # Update import path as needed
from flask import Blueprint, session, g

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('main.login'))

    user_data = session['user']
    user_id = user_data['id']

    badges = get_user_badges(user_id)
    user_data['badges'] = badges

    return render_template("profile.html", user=user_data)