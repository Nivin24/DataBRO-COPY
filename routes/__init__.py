# routes/__init__.py
from flask import Blueprint

# Create a Blueprint instance
main_bp = Blueprint('main', __name__)

# Import route handlers so they're registered
from . import profile, settings, dashboard, editor, api