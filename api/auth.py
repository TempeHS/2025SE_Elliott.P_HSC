<<<<<<< HEAD
from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from api.data_management import validate_signup_data, validate_login_data
from logger_config import logger

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login_page():
    logger.debug('login page accessed')
    return render_template('login.html')

@auth_bp.route('/signup')
def signup_page():
    logger.debug('signup page accessed')
    return render_template('signup.html')

@auth_bp.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    logger.debug('signup data: %s', data)
    errors = validate_signup_data(data)
    if errors:
        logger.debug('signup errors: %s', errors)
        return jsonify({'errors': errors}), 400

    if User.query.filter_by(email=data['email']).first():
        logger.debug('signup error: email already registered')
        return jsonify({'error': 'Email already registered'}), 400

    user = User(
        email=data['email'],
        password_hash=generate_password_hash(data['password'])
    )
    db.session.add(user)
    db.session.commit()

    session['user_id'] = user.id
    logger.debug('signup successful for user: %s', user.email)
    return jsonify({'message': 'Registration successful', 'redirect': url_for('index')})

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    logger.debug('login request (%s) email [%s] password [%s]', request.method, data["email"], data["password"])
    errors = validate_login_data(data)
    if errors:
        logger.debug('login errors: %s', errors)
        return jsonify({'errors': errors}), 400

    user = User.query.filter_by(email=data['email']).first()

    if user and check_password_hash(user.password_hash, data['password']):
        session['user_id'] = user.id
        logger.debug('login successful for user: %s', user.email)
        return jsonify({'message': 'Login successful', 'redirect': url_for('index')})

    logger.debug('login error: invalid credentials')
    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    logger.debug('logout successful')
    return jsonify({'message': 'Logout successful'})

@auth_bp.route('/api/user')
def get_user():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        logger.debug('get user: %s', user.email)
        return jsonify({'email': user.email})
    logger.debug('get user error: not authenticated')
    return jsonify({'error': 'Not authenticated'}), 401

#handles session management!
#and user authenications
=======
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
>>>>>>> fork/main
