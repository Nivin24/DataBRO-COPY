from flask import Blueprint, render_template

contact_bp = Blueprint('contact_bp', __name__)

@contact_bp.route('/contact')
def contact():
    return render_template('contact.html')