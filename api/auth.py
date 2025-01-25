from flask import jsonify, request, session
from flask_login import login_user, logout_user
from datetime import datetime
from models import db, User
from . import api
from .data_manager import DataManager
from .user_manager import UserManager
import random
import string
from flask_mail import Mail, Message
mail = Mail()

#when get POST request, check credentials and handle errors
@api.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = UserManager.authenticate(data['email'], data['password'])
    
    if user:
        if user.two_fa_enabled:
            code = generate_verification_code()
            session['temp_user_id'] = user.id
            session['verification_code'] = code
            
            msg = Message('Login Verification Code',
                          sender='noreply@devlog.com',
                          recipients=[user.email])
            msg.body = f'Your login verification code is: {code}'
            mail.send(msg)
            
            return jsonify({
                'require_2fa': True,
                'message': 'Please enter verification code'
            })
            
        login_user(user)
        session['user_id'] = user.id
        session['last_active'] = datetime.utcnow().isoformat()
        return jsonify({'redirect': '/'})
        
    return jsonify({'error': 'Invalid credentials'}), 401


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


def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

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
    mail.send(msg)
    
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
    code = request.json.get('code')
    if code == session.get('verification_code'):
        user_id = session.get('temp_user_id')
        user = User.query.get(user_id)
        if user:
            login_user(user)
            session['user_id'] = user.id
            session['last_active'] = datetime.utcnow().isoformat()
            session.pop('verification_code', None)
            session.pop('temp_user_id', None)
            return jsonify({'redirect': '/'})
    return jsonify({'error': 'Invalid verification code'}), 401
