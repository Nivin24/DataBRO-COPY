# utils.py
from collections import defaultdict
from datetime import timedelta
from calendar import monthrange
from models import db, UserActivity # or from models if you keep models separately
import requests

def get_user_badges(user_id):
    logs = UserActivity.query.filter_by(user_id=user_id).all()
    if not logs:
        return []

    dates = sorted([log.activity_date for log in logs])
    badges = set()

    # Total activity
    if len(dates) >= 50:
        badges.add("50days")
    if len(dates) >= 100:
        badges.add("100days")

    # Streak
    streak = 1
    longest = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            streak += 1
            longest = max(longest, streak)
        elif dates[i] != dates[i - 1]:
            streak = 1
    if longest >= 30:
        badges.add("30days")

    # Full-month badge
    calendar = defaultdict(set)
    for d in dates:
        calendar[(d.year, d.month)].add(d.day)

    for (year, month), days_set in calendar.items():
        _, total_days = monthrange(year, month)
        if len(days_set) == total_days:
            badges.add("full-month")
            break

    return list(badges)
# def get_user_badges(user_id):
#     # ⛔ TEMP for testing only!
#     return ["30days", "full-month"]



# 🆕 New function for geolocation
def get_geolocation(ip_address):
    try:
        response = requests.get(f'https://ipinfo.io/{ip_address}/json')
        data = response.json()
        location = {}

        # Latitude and Longitude
        if 'loc' in data:
            latitude, longitude = map(float, data['loc'].split(','))
            location['latitude'] = latitude
            location['longitude'] = longitude

        # Optional location fields
        location['city'] = data.get('city')
        location['country'] = data.get('country')
        location['method'] = 'ip'

        return location
    except Exception as e:
        print(f"[ERROR] Geolocation fetch failed: {e}")
        return None