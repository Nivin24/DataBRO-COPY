from flask import render_template
from flask import Blueprint, session, g

error_handlers_bp = Blueprint('error_handlers', __name__)

@error_handlers_bp.route('/page_not_found')
def page_not_found(e):
    return render_template('404.html'), 404