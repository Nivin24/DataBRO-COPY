# routes/settings.py
from flask import session, redirect, url_for, render_template, request, flash
from flask_wtf.csrf import generate_csrf
from . import main_bp
from flask import Blueprint, session, g

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    user = session.get('user')
    if not user:
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        updated_user = user.copy()
        updated_user['email'] = request.form.get('email')
        updated_user['username'] = request.form.get('username')
        updated_user['bio'] = request.form.get('bio')
        session['user'] = updated_user
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('main.settings'))

    csrf_token = generate_csrf()
    return render_template('settings.html', user=user, csrf_token=csrf_token)