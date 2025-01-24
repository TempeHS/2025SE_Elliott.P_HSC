from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    developer_tag = db.Column(db.String(50), unique=True, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class LogEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    repository_url = db.Column(db.String(500))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    time_worked = db.Column(db.Integer)  # Store minutes
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    developer_tag = db.Column(db.String(50), db.ForeignKey('user.developer_tag'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'project': self.project,
            'content': self.content,
            'repository_url': self.repository_url,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'time_worked': self.time_worked,
            'timestamp': self.timestamp.isoformat(),
            'developer_tag': self.developer_tag
        }
