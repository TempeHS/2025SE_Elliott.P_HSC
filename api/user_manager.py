from flask import session
from datetime import datetime, timedelta
from models import User, LogEntry, db
from .data_manager import DataManager

# user authentication and session management

class UserManager:
    # handles login checks and session management
    SESSION_TIMEOUT = timedelta(hours=1)

    @staticmethod
    def authenticate(email, password):
        print(f"Authentication attempt for email: {email}")
        email = DataManager.sanitize_email(email)
        user = User.query.filter_by(email=email).first()
        print(f"User found: {user}")
        if user and user.check_password(password):
            print("Password check passed")
            return user

        print("Authentication failed")
        return None

    # creates new users safely
    @staticmethod
    def create_user(email, password, developer_tag):
        email = DataManager.sanitize_email(email)
        developer_tag = DataManager.sanitize_developer_tag(developer_tag)
        
        if User.query.filter_by(email=email).first():
            raise ValueError("Email already registered")
        if User.query.filter_by(developer_tag=developer_tag).first():
            raise ValueError("Developer tag already taken")
        
        user = User(email=email, developer_tag=developer_tag)
        user.set_password(password)
        db.session.add(user)
        return user

#check if session is legit and not expired
    @staticmethod
    def check_session():
        if 'user_id' not in session:
            return False
        if 'last_active' not in session:
            return False
        
        last_active = datetime.fromisoformat(session['last_active'])
        if datetime.utcnow() - last_active > UserManager.SESSION_TIMEOUT:
            session.clear()
            return False
            
        session['last_active'] = datetime.utcnow().isoformat()
        return True

    @staticmethod
    def get_current_user():
        if not UserManager.check_session():
            return None
        return User.query.get(session['user_id'])

    @staticmethod
    def download_user_data(user):
        entries = LogEntry.query.filter_by(developer_tag=user.developer_tag).all()
        return {
            'user': {
                'email': user.email,
                'developer_tag': user.developer_tag
            },
            'entries': [entry.to_dict() for entry in entries]
        }

    @staticmethod
    def delete_user_account(user):
        LogEntry.query.filter_by(developer_tag=user.developer_tag).delete()
        db.session.delete(user)
        db.session.commit()
