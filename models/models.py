from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    developer_tag = db.Column(db.String(50), unique=True, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f'<User {self.email}>'

class LogEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    developer_tag = db.Column(db.String(50), db.ForeignKey('user.developer_tag'), nullable=False)

    def __repr__(self):
        return f'<LogEntry {self.project} by {self.developer_tag}>'

    def to_dict(self):
        return {
            'id': self.id,
            'project': self.project,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'developer_tag': self.developer_tag
        }