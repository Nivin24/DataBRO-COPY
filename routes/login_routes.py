# routes/login_routes.py

from flask import Blueprint, session, redirect, url_for, request
from requests_oauthlib import OAuth2Session
from models import db, User, UserActivity
from datetime import datetime, timedelta, timezone
from utils import get_user_badges, get_geolocation
import jwt, os, traceback

login_bp = Blueprint('login', __name__)

client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://oauth2.googleapis.com/token"
userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
scope = ["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email"]
JWT_SECRET = os.getenv("JWT_SECRET_KEY")

@login_bp.route('/login')
def login():
    session['next_url'] = request.args.get('next')
    redirect_uri = url_for('login.callback', _external=True)
    google = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)
    authorization_url, state = google.authorization_url(authorization_base_url, access_type='offline', prompt='select_account')
    session['oauth_state'] = state
    return redirect(authorization_url)

@login_bp.route('/login/callback')
def callback():
    try:
        if 'oauth_state' not in session:
            return redirect(url_for('login.login'))

        redirect_uri = url_for('login.callback', _external=True)
        google = OAuth2Session(client_id, redirect_uri=redirect_uri, state=session['oauth_state'])
        token = google.fetch_token(token_url, client_secret=client_secret, authorization_response=request.url, include_client_id=True)
        session['oauth_token'] = token

        resp = google.get(userinfo_url)
        user_data = resp.json()

        user = User.query.filter_by(google_id=user_data["id"]).first()
        if not user:
            # New signup
            ip_address = request.remote_addr
            location_data = get_geolocation(ip_address) or {}

            user = User(
                google_id=user_data["id"],
                name=user_data["name"],
                email=user_data["email"],
                picture=user_data["picture"],
                signup_date=datetime.now(timezone.utc),
                bio='This is a sample bio.',
                last_location_ip=ip_address,
                last_location_lat=location_data.get('latitude'),
                last_location_lon=location_data.get('longitude'),
                last_location_city=location_data.get('city'),
                last_location_country=location_data.get('country'),
                last_location_method=location_data.get('method', 'ip'),
                last_location_date=datetime.now(timezone.utc).date()
            )
            db.session.add(user)
            db.session.commit()

        # Update geolocation on every login
        ip_address = request.remote_addr
        location_data = get_geolocation(ip_address) or {}

        user.last_location_ip = ip_address
        user.last_location_lat = location_data.get('latitude')
        user.last_location_lon = location_data.get('longitude')
        user.last_location_city = location_data.get('city')
        user.last_location_country = location_data.get('country')
        user.last_location_method = location_data.get('method', 'ip')
        user.last_location_date = datetime.now(timezone.utc).date()

        db.session.commit()

        session['user'] = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "picture": user.picture,
            "signup_date": user.signup_date,
            "bio": user.bio
        }
        session['email'] = user.email.strip().lower()

        today_utc = datetime.now(timezone.utc).date()
        existing = UserActivity.query.filter_by(user_id=user.id, activity_date=today_utc).first()
        if not existing:
            db.session.add(UserActivity(user_id=user.id, activity_date=today_utc))
            db.session.commit()

        badges = get_user_badges(user.id)
        user.badges = badges
        db.session.commit()

        payload = {
            "user_id": user.id,
            "email": user.email,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        session['jwt'] = token

        next_url = session.pop('next_url', None)
        return redirect(next_url or url_for('home.home'))
    
    except Exception as e:
        traceback.print_exc()
        return f"OAuth Error: {e}", 403

@login_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('home.home'))