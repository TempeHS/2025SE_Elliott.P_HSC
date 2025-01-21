from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
<<<<<<< HEAD
    password_hash = db.Column(db.String(128), nullable=False)
    log_entries = db.relationship('LogEntry', backref='developer', lazy=True)
=======
    password_hash = db.Column(db.String(128))
    developer_tag = db.Column(db.String(50), unique=True, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
>>>>>>> fork/main

class LogEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    developer_id = db.Column(db.Integer, db.ForeignKey('user.id'))

<<<<<<< HEAD
#sets up the database and database entry stuff, with limitations on entry length and required fields
=======
    def to_dict(self):
        return {
            'id': self.id,
            'project': self.project,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'developer_tag': self.developer_tag
        }
>>>>>>> fork/main
