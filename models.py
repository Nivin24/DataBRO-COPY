from extensions import db
from datetime import datetime, timezone, date
from sqlalchemy.dialects.sqlite import JSON


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(128), unique=True, nullable=False)
    name = db.Column(db.String(128))
    email = db.Column(db.String(128))
    picture = db.Column(db.String(256))
    signup_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    bio = db.Column(db.String(300))
    badges = db.Column(JSON, default=list)
    
    # New location fields
    last_location_lat = db.Column(db.String(64))
    last_location_lon = db.Column(db.String(64))
    last_location_city = db.Column(db.String(128))
    last_location_country = db.Column(db.String(128))
    last_location_ip = db.Column(db.String(64))
    last_location_method = db.Column(db.String(32))  # "gps" or "ip"
    last_location_date = db.Column(db.Date)

class UserActivity(db.Model):
    __tablename__ = 'user_activity'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_date = db.Column(db.Date, default=datetime.now(timezone.utc).date())

    __table_args__ = (
        db.UniqueConstraint('user_id', 'activity_date', name='unique_user_activity'),
    )
    
class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    display_order = db.Column(db.Integer, default=0)
    
class TopicContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    theory = db.Column(db.Text)
    quiz = db.Column(db.Text)
    flashcards = db.Column(db.Text)
    resources = db.Column(db.Text)
    certifications = db.Column(db.Text)
    practical = db.Column(db.Text)

    topic = db.relationship('Topic', backref=db.backref('content', uselist=False, cascade='all, delete-orphan'))