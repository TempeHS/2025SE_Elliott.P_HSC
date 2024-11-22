from flask import jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from . import api
import re
import sys

@api.route('/auth/signup', methods=['POST'])
def signup():
    print("request received at /api/auth/signup", file=sys.stdout)
    print(f"request headers: {dict(request.headers)}", file=sys.stdout)
    print(f"request method: {request.method}", file=sys.stdout)
    
    try:
        data = request.get_json()
        print(f"received data: {data}", file=sys.stdout)
    except Exception as e:
        print(f"error parsing JSON: {e}", file=sys.stdout)
        return jsonify({'error': 'invalid JSON data'}), 400

    email = data.get('email')
    password = data.get('password')
    developer_tag = data.get('developer_tag')

    if not email or not password or not developer_tag:
        print("validation failed: missing email, password, or developer tag", file=sys.stdout)
        return jsonify({'error': 'email, password, and developer tag are required'}), 400

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        print("validation failed: invalid email format", file=sys.stdout)
        return jsonify({'error': 'invalid email format'}), 400

    if len(password) < 8 or not re.search(r"\d", password):
        print("validation failed: password requirements not met", file=sys.stdout)
        return jsonify({'error': 'password must be at least 8 characters long and contain at least one number'}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        print("validation failed: email already registered", file=sys.stdout)
        return jsonify({'error': 'email already registered'}), 400

    existing_tag = User.query.filter_by(developer_tag=developer_tag).first()
    if existing_tag:
        print("validation failed: developer tag already registered", file=sys.stdout)
        return jsonify({'error': 'developer tag already registered'}), 400

    try:
        new_user = User(
            email=email,
            password_hash=generate_password_hash(password),
            developer_tag=developer_tag
        )
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        print(f"user created: {email}", file=sys.stdout)
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
    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        print(f"login successful for: {email}", file=sys.stdout)
        return jsonify({'message': 'login successful', 'email': user.email})

    print("login failed: invalid credentials", file=sys.stdout)
    return jsonify({'error': 'invalid email or password'}), 401

@api.route('/auth/user', methods=['GET'])
def get_current_user():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return jsonify({'email': user.email})
    return jsonify({'error': 'unauthorized'}), 401
