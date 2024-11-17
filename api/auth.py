from flask import jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from . import api
import sys

@api.route('/auth/signup', methods=['POST'])
def signup():
    # Print raw request data
    print("request received at /api/auth/signup", file=sys.stdout)
    print(f"request headers: {dict(request.headers)}", file=sys.stdout)
    print(f"request method: {request.method}", file=sys.stdout)
    
    # Get and validate JSON data
    try:
        data = request.get_json()
        print(f"received data: {data}", file=sys.stdout)
    except Exception as e:
        print(f"error parsing JSON: {e}", file=sys.stdout)
        return jsonify({'error': 'invalid JSON data'}), 400

    # Validate required fields
    email = data.get('email') if data else None
    password = data.get('password') if data else None
    
    print(f"extracted email: {email}", file=sys.stdout)
    print(f"password : {'yes' if password else 'bo'}", file=sys.stdout)

    if not email or not password:
        print("validation failed: mssing email or password", file=sys.stdout)
        return jsonify({'error': 'email and password are required'}), 400

    # Check existing user
    existing_user = User.query.filter_by(email=email).first()
    print(f"existing user check: {'found' if existing_user else 'not found'}", file=sys.stdout)
    
    if existing_user:
        return jsonify({'error': 'email already registered'}), 400

    # Create new user
    try:
        new_user = User(
            email=email,
            password_hash=generate_password_hash(password)
        )
        print("user object created", file=sys.stdout)
        
        db.session.add(new_user)
        print("user added to session", file=sys.stdout)
        
        db.session.commit()
        print("database commit successful", file=sys.stdout)
        
        session['user_id'] = new_user.id
        print(f"session created for user: {email}", file=sys.stdout)
        
        return jsonify({'message': 'registration successful', 'email': email})
        
    except Exception as e:
        db.session.rollback()
        print(f"database error occurred: {str(e)}", file=sys.stdout)
        return jsonify({'error': 'failed to create user'}), 500

@api.route('/auth/login', methods=['POST'])
def login():
    print("request received at /api/auth/login", file=sys.stdout)
    print(f"request headers: {dict(request.headers)}", file=sys.stdout)
    print(f"request method: {request.method}", file=sys.stdout)

    try:
        data = request.get_json()
        print(f"received login attempt for email: {data.get('email')}", file=sys.stdout)
    except Exception as e:
        print(f"error parsing JSON: {e}", file=sys.stdout)
        return jsonify({'error': 'invalid JSON data'}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        print("login failed: missing credentials", file=sys.stdout)
        return jsonify({'error': 'email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    print(f"User lookup result: {'Found' if user else 'Not found'}", file=sys.stdout)

    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        print(f"login successful for : {email}", file=sys.stdout)
        return jsonify({
            'message': 'Login successful',
            'email': user.email
        })

    print("login failed: invalid credentials", file=sys.stdout)
    return jsonify({'error': 'invalid email or password'}), 401

@api.route('/auth/user', methods=['GET'])
def get_current_user():
    print("Request received at /api/auth/user", file=sys.stdout)
    print(f"Session data: {session}", file=sys.stdout)
    
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            print(f"Found user: {user.email}", file=sys.stdout)
            return jsonify({
                'authenticated': True,
                'email': user.email
            })
        print("user in session but user not found in database", file=sys.stdout)
    
    print("no user found (401(good))", file=sys.stdout)
    return jsonify({'authenticated': False}), 401
