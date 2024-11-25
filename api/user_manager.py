from flask_login import login_user, logout_user
from models import User
from .data_manager import DataManager

class UserManagement:
    @staticmethod
    def authenticate(email, password):
        email = DataManager.sanitize_email(email)
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            return user
        return None

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
        return user

    @staticmethod
    def login_user(user):
        login_user(user)

    @staticmethod
    def logout_user():
        logout_user()