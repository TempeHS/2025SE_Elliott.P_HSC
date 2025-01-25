from flask import jsonify, request, session
from flask_login import login_user, logout_user
from datetime import datetime
from models import db
from . import api
from .data_manager import DataManager
from .user_manager import UserManager

#when get POST request, check credentials and handle errors
@api.route('/auth/login', methods=['POST'])
def login():
    print("Login attempt received")
    try:
        data = request.get_json()
        print(f"Login data received: {data}")
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Missing credentials'}), 400
            
        user = UserManager.authenticate(data['email'], data['password'])
        
        if user:
            login_user(user)
            session['user_id'] = user.id
            session['last_active'] = datetime.utcnow().isoformat()
            print(f"Login successful for user: {user.email}")
            return jsonify({'message': 'Login successful', 'redirect': '/'})
            
        return jsonify({'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': str(e)}), 400

#when get POST request, validate data and create new user
@api.route('/auth/signup', methods=['POST'])
def signup():
    print("Signup attempt received")
    try:
        data = request.get_json()
        print(f"Signup data received: {data}")
        
        if not all(k in data for k in ['email', 'password', 'developer_tag']):
            return jsonify({'error': 'Missing required fields'}), 400

        user = UserManager.create_user(
            email=data['email'],
            password=data['password'],
            developer_tag=data['developer_tag']
        )
        
        db.session.commit()
        
        login_user(user)
        session['user_id'] = user.id
        session['last_active'] = datetime.utcnow().isoformat()
        print(f"Signup successful for user: {user.email}")
        return jsonify({'message': 'Registration successful', 'redirect': '/'})
        
    except Exception as e:
        db.session.rollback()
        print(f"Signup error: {str(e)}")
        return jsonify({'error': str(e)}), 400

#havent implemented yet !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@api.route('/auth/logout', methods=['POST'])
def logout():
    try:
        logout_user()
        session.clear()
        return jsonify({'message': 'Logged out successfully', 'redirect': '/login'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api.route('/user/data', methods=['GET'])
def get_user_data():
    user = UserManager.get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
        
    user_data = UserManager.download_user_data(user)
    return jsonify(user_data)

@api.route('/user/data', methods=['DELETE'])
def delete_user_data():
    user = UserManager.get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
        
    UserManager.delete_user_account(user)
    return jsonify({'message': 'Account deleted successfully'})
