from flask import jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from . import api

@api.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    print("Received signup data:", data)  # Debug line
    
    # Validate incoming data
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    user = User(
        email=data['email'],
        password_hash=generate_password_hash(data['password'])
    )
    db.session.add(user)
    db.session.commit()
    
    session['user_id'] = user.id
    return jsonify({'message': 'Registration successful'})
