from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    developer_tag = db.Column(db.String(50), unique=True, nullable=False)

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
