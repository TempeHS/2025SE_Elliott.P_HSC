from flask import jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from . import api
import sys

@api.route('/auth/signup', methods=['POST'])
def signup():
    # Print raw request data
    print("Request received at /api/auth/signup", file=sys.stdout)
    print(f"Request headers: {dict(request.headers)}", file=sys.stdout)
    print(f"Request method: {request.method}", file=sys.stdout)
    
    # Get and validate JSON data
    try:
        data = request.get_json()
        print(f"Received data: {data}", file=sys.stdout)
    except Exception as e:
        print(f"Error parsing JSON: {e}", file=sys.stdout)
        return jsonify({'error': 'Invalid JSON data'}), 400

    # Validate required fields
    email = data.get('email') if data else None
    password = data.get('password') if data else None
    
    print(f"Extracted email: {email}", file=sys.stdout)
    print(f"Password received: {'Yes' if password else 'No'}", file=sys.stdout)

    if not email or not password:
        print("Validation failed: Missing email or password", file=sys.stdout)
        return jsonify({'error': 'Email and password are required'}), 400

    # Check existing user
    existing_user = User.query.filter_by(email=email).first()
    print(f"Existing user check: {'Found' if existing_user else 'Not found'}", file=sys.stdout)
    
    if existing_user:
        return jsonify({'error': 'Email already registered'}), 400

    # Create new user
    try:
        new_user = User(
            email=email,
            password_hash=generate_password_hash(password)
        )
        print("User object created", file=sys.stdout)
        
        db.session.add(new_user)
        print("User added to session", file=sys.stdout)
        
        db.session.commit()
        print("Database commit successful", file=sys.stdout)
        
        session['user_id'] = new_user.id
        print(f"Session created for user: {email}", file=sys.stdout)
        
        return jsonify({'message': 'Registration successful', 'email': email})
        
    except Exception as e:
        db.session.rollback()
        print(f"Database error occurred: {str(e)}", file=sys.stdout)
        return jsonify({'error': 'Failed to create user'}), 500

@api.route('/auth/login', methods=['POST'])
def login():
    print("Request received at /api/auth/login", file=sys.stdout)
    print(f"Request headers: {dict(request.headers)}", file=sys.stdout)
    print(f"Request method: {request.method}", file=sys.stdout)

    try:
        data = request.get_json()
        print(f"Received login attempt for email: {data.get('email')}", file=sys.stdout)
    except Exception as e:
        print(f"Error parsing JSON: {e}", file=sys.stdout)
        return jsonify({'error': 'Invalid JSON data'}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        print("Login failed: Missing credentials", file=sys.stdout)
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    print(f"User lookup result: {'Found' if user else 'Not found'}", file=sys.stdout)

    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        print(f"Login successful for user: {email}", file=sys.stdout)
        return jsonify({
            'message': 'Login successful',
            'email': user.email
        })

    print("Login failed: Invalid credentials", file=sys.stdout)
    return jsonify({'error': 'Invalid email or password'}), 401

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
        print("User ID in session but user not found in database", file=sys.stdout)
    
    print("No authenticated user found", file=sys.stdout)
    return jsonify({'authenticated': False}), 401
