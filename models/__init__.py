import bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.LargeBinary) 
    developer_tag = db.Column(db.String(50), unique=True, nullable=False)
    two_fa_enabled = db.Column(db.Boolean, default=False)
    two_fa_verified = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)

def check_password(self, password):
    return bcrypt.checkpw(
        password.encode('utf-8'), 
        self.password_hash.encode('utf-8')
    )

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
    two_fa_enabled = db.Column(db.Boolean, default=False)
    two_fa_verified = db.Column(db.Boolean, default=False)

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
