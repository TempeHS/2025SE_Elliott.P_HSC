from flask import jsonify, request, session
from flask_login import login_user, logout_user
from models import User, db
from . import api
from .user_manager import UserManagement

@api.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Missing credentials'}), 400
            
        user = UserManagement.authenticate(data['email'], data['password'])
        
        if user:
            UserManagement.login_user(user)
            session['user_id'] = user.id  # Assign user ID to session
            return jsonify({'message': 'Login successful', 'redirect': '/'})
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api.route('/auth/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        if not all(k in data for k in ['email', 'password', 'developer_tag']):
            return jsonify({'error': 'Missing required fields'}), 400
            
        user = UserManagement.create_user(
            email=data['email'],
            password=data['password'],
            developer_tag=data['developer_tag']
        )
        
        db.session.add(user)
        db.session.commit()
        
        UserManagement.login_user(user)
        session['user_id'] = user.id  # Assign user ID to session
        return jsonify({'message': 'Registration successful', 'redirect': '/'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@api.route('/auth/logout', methods=['POST'])
def logout():
    try:
        UserManagement.logout_user()
        session.clear()
        return jsonify({'message': 'Logged out successfully', 'redirect': '/login'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400