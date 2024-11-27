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
        return jsonify({'error': 'email already registered'}), 400

    user = User(
        email=data['email'],
        password_hash=generate_password_hash(data['password'])
    )
    db.session.add(user)
    db.session.commit()

    session['user_id'] = user.id
    logger.debug('signup successful for user: %s', user.email)
    return jsonify({'message': 'registration successful', 'redirect': url_for('index')})

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
        return jsonify({'message': 'login successful', 'redirect': url_for('index')})

    logger.debug('login error: invalid credentials')
    return jsonify({'error': 'invalid credentials'}), 401

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    logger.debug('logout successful')
    return jsonify({'message': 'logout successful'})

@auth_bp.route('/api/user')
def get_user():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        logger.debug('get user: %s', user.email)
        return jsonify({'email': user.email})
    logger.debug('get user error: not authenticated')
    return jsonify({'error': 'not authenticated'}), 401