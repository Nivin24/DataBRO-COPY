# routes/api.py
from flask import jsonify, session
from flask import current_app as app
from . import main_bp
from datetime import datetime, timedelta, timezone, date
from collections import defaultdict, Counter
from models import db, User, UserActivity
from sqlalchemy import func

from flask import Blueprint, session, g

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/dashboard-data')
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
    
    
    
    
@api_bp.route('/api/activity-data')
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
    
    
@api_bp.route('/api/badge-progress')
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