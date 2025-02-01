from flask import jsonify, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from models import db, User
from . import api
from .data_manager import DataManager
from .user_manager import UserManager
from flask_mail import Message
import random
import string
import logging
import time

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@api.route('/auth/login', methods=['POST'])
def login():
    logger.info("Login attempt received")
    
    if not request.is_json:
        return jsonify({'error': 'Invalid content type'}), 400
        
    data = request.get_json()
    if not all(k in data for k in ['email', 'password']):
        return jsonify({'error': 'Missing credentials'}), 400

    try:
        user = UserManager.authenticate(data['email'], data['password'])
        
        if user:
            if user.two_fa_enabled:
                code = generate_verification_code()
                session['temp_user_id'] = user.id
                session['verification_code'] = code
                session['verification_expires'] = time.time() + 300  # 5 minute timeout
                
                msg = Message('Login Verification Code',
                            sender='noreply@devlog.com',
                            recipients=[user.email])
                msg.body = f'Your verification code is: {code}'
                current_app.extensions['mail'].send(msg)
                
                logger.info(f"2FA code sent to user: {user.email}")
                return jsonify({
                    'require_2fa': True,
                    'message': 'Please enter verification code',
                    'expires_in': 300
                })
                
            login_user(user)
            session['user_id'] = user.id
            session['last_active'] = datetime.utcnow().isoformat()
            return jsonify({'redirect': '/'})
            
        return jsonify({'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

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

@api.route('/auth/logout', methods=['POST'])
def logout():
    try:
        logout_user()
        session.clear()
        return jsonify({'message': 'Logged out successfully', 'redirect': '/login'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api.route('/auth/enable-2fa', methods=['POST'])
def enable_2fa():
    user = UserManager.get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401

    code = generate_verification_code()
    session['verification_code'] = code
    
    msg = Message('Your Verification Code',
                  sender='noreply@devlog.com',
                  recipients=[user.email])
    msg.body = f'Your verification code is: {code}'
    current_app.extensions['mail'].send(msg)
    
    return jsonify({'message': 'Verification code sent'})

@api.route('/auth/disable-2fa', methods=['POST'])
def disable_2fa():
    user = UserManager.get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
        
    user.two_fa_enabled = False
    user.two_fa_verified = False
    db.session.commit()
    return jsonify({'message': '2FA disabled successfully'})

@api.route('/auth/verify-2fa', methods=['POST'])
def verify_2fa():
    user = UserManager.get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401

    code = request.json.get('code')
    if code == session.get('verification_code'):
        user.two_fa_enabled = True
        user.two_fa_verified = True
        db.session.commit()
        session.pop('verification_code', None)
        return jsonify({'message': '2FA enabled successfully'})
    
    return jsonify({'error': 'Invalid verification code'}), 400

@api.route('/auth/verify-login', methods=['POST'])
def verify_login():
    logger.info("Verification attempt received")
    
    code = request.json.get('code')
    stored_code = session.get('verification_code')
    temp_user_id = session.get('temp_user_id')
    
    logger.info(f"Received verification code: {code}")
    logger.info(f"Stored verification code: {stored_code}")
    logger.info(f"Temporary user ID: {temp_user_id}")
    logger.info(f"Current session data: {dict(session)}")

    if code == stored_code and temp_user_id:
        user = User.query.get(temp_user_id)
        if user:
            login_user(user)
            session['user_id'] = user.id
            session['last_active'] = datetime.utcnow().isoformat()
            
            session.pop('verification_code', None)
            session.pop('temp_user_id', None)
            
            logger.info(f"User {user.email} successfully verified and logged in")
            return jsonify({'redirect': '/'})
            
        logger.warning("User not found for temp_user_id")
    else:
        logger.warning("Code mismatch or missing temp_user_id")
        
    return jsonify({'error': 'Invalid verification code'}), 401

@api.route('/user/generate-key', methods=['POST'])
@login_required
def generate_api_key():
    try:
        key = current_user.generate_api_key()
        db.session.commit()
        return jsonify({'message': 'API key generated', 'key': key})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/auth/api-key', methods=['POST'])
def api_authenticate():
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return jsonify({'error': 'No API key provided'}), 401
    user = User.query.filter_by(api_key=api_key, api_enabled=True).first()
    if not user:
        return jsonify({'error': 'Invalid API key'}), 401
    return jsonify({'authenticated': True})