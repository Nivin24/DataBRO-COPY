import os
from flask import Flask, render_template, redirect, url_for, session, request, flash, g, jsonify
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
from models import db, User, UserActivity
import jwt
from flask import g, session, request
from datetime import datetime, timedelta, timezone, date
import traceback
from flask_session import Session
from utils import get_user_badges
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy import func, extract
from collections import defaultdict, Counter
import collections # For Counter
from utils import get_user_badges  # Make sure this import is at the top of your file
from models import Topic


# Load environment variables
load_dotenv()

# Allow OAuth over HTTP (only for development)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # NO need in production

# Initialize app
app = Flask(__name__)

# DB config must come before init_app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from models import db
db.init_app(app)

from flask_migrate import Migrate
migrate = Migrate(app, db)

# Session configuration (ensure to set secure cookies in production)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False # Make this True for Production
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './flask_session'
app.config['SESSION_PERMANENT'] = False

Session(app)
# Secret key for session management
app.secret_key = os.getenv("SECRET_KEY")


@app.before_request
def log_daily_user_activity():
    user = session.get('user')
    if not user:
        return  # Not logged in

    if request.endpoint in ('static',):  # Avoid logging for static file requests
        return

    # Ensure we only log once per request cycle
    if hasattr(g, 'activity_checked'):
        return
    g.activity_checked = True

    today_utc = datetime.now(timezone.utc).date()  # ✅ Use UTC date
    existing = UserActivity.query.filter_by(user_id=user['id'], activity_date=today_utc).first()
    if not existing:
        db.session.add(UserActivity(user_id=user['id'], activity_date=today_utc))
        db.session.commit()

@app.before_request
def assign_badges_if_logged_in():
    user = session.get('user')
    if user:
        user_id = user['id']
        badges = get_user_badges(user_id)
        user['badges'] = badges
        session['user'] = user

        db_user = db.session.get(User, user_id)
        if db_user and db_user.badges != badges:
            db_user.badges = badges
            db.session.commit()


# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SUPABASE_DB_URL")

# db = SQLAlchemy(app)

# Initialize the database
db_path = os.path.join(os.getcwd(), 'users.db')
if not os.path.exists(db_path):
    with app.app_context():
        db.create_all()
        print("Database initialized successfully.")
else:
    print("Database already exists.")

# Google OAuth setup
client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://oauth2.googleapis.com/token"
userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
scope = ["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email"]

# JWT secret
JWT_SECRET = os.getenv("JWT_SECRET_KEY")


# # User model
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     google_id = db.Column(db.String(128), unique=True, nullable=False)
#     name = db.Column(db.String(128))
#     email = db.Column(db.String(128))
#     picture = db.Column(db.String(256))
#     signup_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
#     bio = db.Column(db.String(300))
#     badges = db.Column(JSON, default=list)
    
# # New
# class UserActivity(db.Model):
#     __tablename__ = 'user_activity'
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     activity_date = db.Column(db.Date, default=datetime.utcnow().date)

#     __table_args__ = (
#         db.UniqueConstraint('user_id', 'activity_date', name='unique_user_activity'),
#     )

@app.route('/login')
def login():
    next_url = request.args.get('next')
    session['next_url'] = next_url  # Save for after callback
    #chumma
    redirect_uri = url_for('callback', _external=True)
    
    google = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)
    authorization_url, state = google.authorization_url(authorization_base_url, access_type='offline', prompt='select_account')
    session['oauth_state'] = state
    return redirect(authorization_url)


@app.route('/login/callback')
def callback():
    try:
        if 'oauth_state' not in session:
            print("Missing 'oauth_state' in session. Possible session loss.")
            return redirect(url_for('login'))  # Redirect instead of 403
        redirect_uri = url_for('callback', _external=True)
        google = OAuth2Session(client_id, redirect_uri=redirect_uri, state=session['oauth_state'])

        token = google.fetch_token(token_url, client_secret=client_secret, authorization_response=request.url, include_client_id=True)

        session['oauth_token'] = token
        resp = google.get(userinfo_url)
        user_data = resp.json()

        # Check if user exists
        user = User.query.filter_by(google_id=user_data["id"]).first()
        if not user:
            user = User(
                google_id=user_data["id"],
                name=user_data["name"],
                email=user_data["email"],
                picture=user_data["picture"],
                signup_date=datetime.now(timezone.utc),
                bio='This is a sample bio.'
            )
            db.session.add(user)
            db.session.commit()

            
        # Save user info in session
        session['user'] = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "picture": user.picture,
            "signup_date": user.signup_date if user.signup_date else datetime.now(timezone.utc),
            "bio": user.bio
        }
        
        # ✅ Normalize and store email separately in session for consistent use
        session['email'] = user.email.strip().lower()
        # Log user activity
        today_utc = datetime.now(timezone.utc).date()
        existing = UserActivity.query.filter_by(user_id=user.id, activity_date=today_utc).first()
        if not existing:
            db.session.add(UserActivity(user_id=user.id, activity_date=today_utc))
            db.session.commit()

        badges = get_user_badges(user.id)
        user.badges = badges
        db.session.commit()

        # Generate JWT token
        payload = {
            "user_id": user.id,
            "email": user.email,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        session['jwt'] = token
        # After login
        next_url = session.pop('next_url', None)
        if next_url:
            return redirect(next_url)
        return redirect(url_for('home'))
    
    except Exception as e:
        traceback.print_exc()
        return f"OAuth Error: {e}", 403
    
    # debug
    app.logger.debug(f"Session email after login: {session.get('email')}")
    app.logger.debug(f"User data from Google: {user_data}")


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('home'))

# end
# Topic list and mapping
# topics = [
#     {"name": "Python", "description": "Learn Python programming from basics to advanced."},
#     {"name": "DSA", "description": "Practice Data Structures and Algorithms."},
#     {"name": "Libraries", "description": "Explore libraries like Numpy, Pandas, Matplotlib, and more."},
#     {"name": "Data Wrangling", "description": "Master data cleaning and preprocessing techniques."},
#     {"name": "Statistics", "description": "Understand statistical concepts for data analysis."},
#     {"name": "Probability", "description": "Dive into probability theory and its applications."},
#     {"name": "Linear Algebra", "description": "Learn linear algebra for machine learning and data science."},
#     {"name": "Calculus", "description": "Understand calculus concepts for optimization."},
#     {"name": "Tableau", "description": "Learn Tableau for data visualization."},
#     {"name": "Power BI", "description": "Master Power BI for business intelligence."},
#     {"name": "Power Query", "description": "Master Power Query for Data Cleaning."},
#     {"name": "Design Principles", "description": "Master Design Principles for creating professional dashboards."},
#     {"name": "Interactive Dashboards", "description": "Learn how to create beautiful and informative data visualizations."},
#     {"name": "D3.js ", "description": "Master D3.js for interactive visualizations."},
#     {"name": "Plotly & Dash", "description": "Master Plotly and Dash"}
#     # Add more topics here

# ]

# # Add slug to each topic
# for topic in topics:
#     topic['slug'] = topic['name'].lower().replace(" ", "-")

# Route: Home Page
# @app.route('/')
# def home():
#     user = session.get('user')
#     return render_template('home.html', topics=topics, user=user)

# Testing the working
@app.route('/')
def home():
    user = session.get('user')
    topics = db.session.execute(
        db.select(Topic).order_by(Topic.display_order)
    ).scalars().all()
    return render_template('home.html', topics=topics, user=user)

@app.route('/debug-topics')
def debug_topics():
    topics = db.session.execute(db.select(Topic)).scalars().all()
    return "<br>".join([f"{t.name} - {t.slug}" for t in topics]) or "No topics found."

# original topic slug
# # Route: Subpages using slug
# @app.route('/topic/<slug>')
# def topic_page(slug):
#     user = session.get('user')
#     if not user:
#         # Redirect to login and remember the page the user was trying to access
#         return redirect(url_for('login', next=request.path))

#     # Find topic by slug
#     topic = next((t for t in topics if t['slug'] == slug), None)
#     if topic:
#         try:
#             return render_template(f"{topic['name']}.html", topic_name=topic['name'])
#         except:
#             return render_template('404.html'), 404
#     else:
#         return render_template('404.html'), 404


# Testing topic slug
@app.route('/topic/<slug>')
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

def page_not_found(_):
    return render_template('404.html'), 404

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# @app.route('/profile')
# def profile():
#     user = session.get('user')
#     if not user:
#         return redirect(url_for('login'))
#     return render_template('profile.html', user=user)

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_data = session['user']
    user_id = user_data['id']

    # 🔥 Add badges
    badges = get_user_badges(user_id)
    user_data['badges'] = badges

    return render_template("profile.html", user=user_data)

from flask_wtf.csrf import generate_csrf

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Handle form submission
        updated_user = user.copy()  # Create a copy of the user object
        updated_user['email'] = request.form.get('email')
        updated_user['username'] = request.form.get('username')
        updated_user['bio'] = request.form.get('bio')
        session['user'] = updated_user  # Update session with modified user data
        # Add logic to handle password and notifications if needed
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('settings'))

    # Render the settings page
    csrf_token = generate_csrf()
    return render_template('settings.html', user=user, csrf_token=csrf_token)
# Route: Contact Page
@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/dashboard')
def dashboard():
    user_email = session.get('email')
    app.logger.debug(f"Session email: {user_email}")
    is_admin = False

    if user_email:
        user = db.session.execute(
            db.select(User).filter_by(email=user_email)
        ).scalar_one_or_none()

        admin_emails = ['homepcni03@gmail.com', 'databro.connect@gmail.com']
        app.logger.debug(f"Comparing user email '{user_email}' with admin list: {admin_emails}")

        if user and user.email.strip().lower() in [email.lower() for email in admin_emails]:
            app.logger.debug("User is admin")
            is_admin = True
        else:
            app.logger.debug("User is NOT admin")

    return render_template("dashboard.html", is_admin=is_admin)

@app.context_processor
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


@app.route('/api/dashboard-data')
def get_dashboard_data():
    try:
        today = datetime.now(timezone.utc).date()
        start_30_days = today - timedelta(days=30)
        start_90_days = today - timedelta(days=90)
        start_7_days = today - timedelta(days=7)

        # Total users
        total_users = db.session.query(User.id).count()

        # New signups (last 7 and 30 days)
        new_signups_7_days = db.session.query(User.id).filter(User.signup_date >= datetime.combine(start_7_days, datetime.min.time(), tzinfo=timezone.utc)).count()
        new_signups_30_days = db.session.query(User.id).filter(User.signup_date >= datetime.combine(start_30_days, datetime.min.time(), tzinfo=timezone.utc)).count()

        # Signups over time (daily for last 30 days)
        signups = db.session.query(
            func.date(User.signup_date).label("signup_date"),
            func.count(User.id)
        ).filter(User.signup_date >= datetime.combine(start_30_days, datetime.min.time(), tzinfo=timezone.utc))\
        .group_by(func.date(User.signup_date)).all()
        signup_trend = {s[0]: s[1] for s in signups}

        # DAU (last 30 days)
        activities = db.session.query(
            UserActivity.activity_date,
            UserActivity.user_id
        ).filter(UserActivity.activity_date >= start_30_days).all()

        dau = defaultdict(set)
        for activity in activities:
            date_str = activity.activity_date.strftime('%Y-%m-%d')
            dau[date_str].add(activity.user_id)

        dau_trend = []
        for i in range(31):
            day = start_30_days + timedelta(days=i)
            date_str = day.strftime('%Y-%m-%d')
            dau_trend.append({
                "date": date_str,
                "count": len(dau.get(date_str, set()))
            })

        # WAU/MAU
        wau = defaultdict(set)
        mau = defaultdict(set)

        for activity in activities:
            year, week, _ = activity.activity_date.isocalendar()
            wau[(year, week)].add(activity.user_id)

            ym = (activity.activity_date.year, activity.activity_date.month)
            mau[ym].add(activity.user_id)

        wau_trend = [{"week": f"{w[0]}-W{w[1]}", "count": len(users)} for w, users in sorted(wau.items())]
        mau_trend = [{"month": f"{m[0]}-{m[1]:02}", "count": len(users)} for m, users in sorted(mau.items())]

        # Top 10 active users
        top_users = db.session.query(
            UserActivity.user_id,
            func.count(UserActivity.id).label("activity_count")
        ).group_by(UserActivity.user_id)\
        .order_by(func.count(UserActivity.id).desc())\
        .limit(10).all()

        top_user_info = []
        for uid, count in top_users:
            user = db.session.get(User, uid)
            last_activity = db.session.query(func.max(UserActivity.activity_date))\
                .filter(UserActivity.user_id == uid).scalar()
            top_user_info.append({
                "name": user.name,
                "email": user.email,
                "count": count,
                "last_login": last_activity.strftime('%Y-%m-%d') if last_activity else "Never"
            })

        # Badges distribution
        all_badges = db.session.query(User.badges).all()
        flat_badges = [badge for user in all_badges if user[0] for badge in user[0]]
        badge_counts = Counter(flat_badges)

        badges_distribution = [{"badge": b, "count": c} for b, c in badge_counts.items()]

        # Activity Heatmap (frequency by day)
        heatmap_data = defaultdict(int)
        for activity in activities:
            heatmap_data[activity.activity_date.strftime('%Y-%m-%d')] += 1

        # Recent users (last 10 with last activity)
        last_activity_subq = db.session.query(
            UserActivity.user_id,
            func.max(UserActivity.activity_date).label("last_login")
        ).group_by(UserActivity.user_id).subquery()

        recent_users = db.session.query(
            User.name,
            User.email,
            User.picture,
            User.signup_date,
            last_activity_subq.c.last_login
        ).outerjoin(last_activity_subq, User.id == last_activity_subq.c.user_id)\
        .order_by(User.signup_date.desc())\
        .limit(10).all()

        recent_user_list = []
        for user in recent_users:
            recent_user_list.append({
                "name": user.name,
                "email": user.email,
                "profile_pic": user.picture or "https://via.placeholder.com/40",
                "joined": user.signup_date if isinstance(user.signup_date, str) else user.signup_date.strftime('%Y-%m-%d'),
                "last_login": user.last_login if isinstance(user.last_login, str) else user.last_login.strftime('%Y-%m-%d') if user.last_login else "Never"
            })

        return jsonify({
            "total_users": total_users,
            "new_signups_7": new_signups_7_days,
            "new_signups_30": new_signups_30_days,
            "signup_trend": signup_trend,
            "dau_trend": dau_trend,
            "wau_trend": wau_trend,
            "mau_trend": mau_trend,
            "top_users": top_user_info,
            "badges": badges_distribution,
            "heatmap": heatmap_data,
            "recent_users": recent_user_list
        })

    except Exception as e:
        app.logger.error(f"Error in /api/dashboard-data: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
# end of dashboard api

@app.route('/editor')
def editor():
    user_email = session.get('email')
    app.logger.debug(f"Session email: {user_email}")
    is_admin = False

    if user_email:
        user = db.session.execute(
            db.select(User).filter_by(email=user_email)
        ).scalar_one_or_none()

        admin_emails = ['homepcni03@gmail.com', 'databro.connect@gmail.com']
        app.logger.debug(f"Comparing user email '{user_email}' with admin list: {admin_emails}")

        if user and user.email.strip().lower() in [email.lower() for email in admin_emails]:
            app.logger.debug("User is admin")
            is_admin = True
        else:
            app.logger.debug("User is NOT admin")

    if not is_admin:
        return redirect(url_for('home'))

    topics = db.session.execute(db.select(Topic)).scalars().all()  # Replace `Topic` with your model

    return render_template("admin_editor.html", is_admin=is_admin, topics=topics)

from datetime import datetime, timedelta

@app.route('/api/activity-data')
def get_activity_data():
    user = session.get('user')
    if not user:
        return jsonify({'error': 'Not logged in'}), 401

    six_months_ago = datetime.now(timezone.utc).date() - timedelta(days=180)  # ✅ Use UTC here too

    logs = UserActivity.query.filter(
        UserActivity.user_id == user['id'],
        UserActivity.activity_date >= six_months_ago
    ).all()

    return jsonify({
        'dates': [log.activity_date.isoformat() for log in logs],  # ✅ ISO format
        'total_days': len(logs)
    })

@app.route('/api/badge-progress')
def badge_progress():
    user = session.get('user')
    if not user:
        return jsonify({'error': 'Not logged in'}), 401

    user_id = user['id']
    logs = UserActivity.query.filter_by(user_id=user_id).all()
    dates = sorted([log.activity_date for log in logs])

    if not dates:
        # no activity
        return jsonify({
            'total_active_days': 0,
            'longest_streak': 0,
            'current_streak': 0,
            'monthly_streak_days': 0,
        })

    # Calculate longest streak
    longest = 1
    streak = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            streak += 1
            longest = max(longest, streak)
        elif dates[i] != dates[i - 1]:
            streak = 1

    # Calculate current streak (consecutive days including today)
    today = date.today()
    dates_set = set(dates)
    current_streak = 0
    i = 0
    while (today - timedelta(days=i)) in dates_set:
        current_streak += 1
        i += 1

    # Calculate monthly streak: count consecutive days in current month including today going backward
    month_start = date(today.year, today.month, 1)
    monthly_streak_days = 0
    day_cursor = today
    while day_cursor >= month_start and day_cursor in dates_set:
        monthly_streak_days += 1
        day_cursor -= timedelta(days=1)

    return jsonify({
        'total_active_days': len(dates),
        'longest_streak': longest,
        'current_streak': current_streak,
        'monthly_streak_days': monthly_streak_days,
    })

# for testing
# @app.route('/seed-topics')
# def seed_topics():
#     from models import Topic

#     topics = [
#         {"name": "Python", "description": "Learn Python programming from basics to advanced."},
#         {"name": "DSA", "description": "Practice Data Structures and Algorithms."},
#         {"name": "Libraries", "description": "Explore libraries like Numpy, Pandas, Matplotlib, and more."},
#         {"name": "Data Wrangling", "description": "Master data cleaning and preprocessing techniques."},
#         {"name": "Statistics", "description": "Understand statistical concepts for data analysis."},
#         {"name": "Probability", "description": "Dive into probability theory and its applications."},
#         {"name": "Linear Algebra", "description": "Learn linear algebra for machine learning and data science."},
#         {"name": "Calculus", "description": "Understand calculus concepts for optimization."},
#         {"name": "Tableau", "description": "Learn Tableau for data visualization."},
#         {"name": "Power BI", "description": "Master Power BI for business intelligence."},
#         {"name": "Power Query", "description": "Master Power Query for Data Cleaning."},
#         {"name": "Design Principles", "description": "Master Design Principles for creating professional dashboards."},
#         {"name": "Interactive Dashboards", "description": "Learn how to create beautiful and informative data visualizations."},
#         {"name": "D3.js", "description": "Master D3.js for interactive visualizations."},
#         {"name": "Plotly & Dash", "description": "Master Plotly and Dash"}
#     ]  # same list
    
#     for index, t in enumerate(topics):
#         slug = t['name'].lower().strip().replace(" ", "-")
#         db.session.add(Topic(name=t['name'], slug=slug, description=t['description'], display_order=index))
#     db.session.commit()
#     return "Topics seeded!"
# Run app for deployment
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database and tables created.")
    app.run(debug=True)
    # For production, use Gunicorn to run the app:
    # gunicorn -w 4 -b 0.0.0.0:8000 App:app