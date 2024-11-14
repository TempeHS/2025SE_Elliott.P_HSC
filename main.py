import os
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from models import db, LogEntry, User
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Database setup
basedir = os.path.abspath(os.path.dirname(__file__))
os.makedirs('.databaseFiles', exist_ok=True)
db_path = os.path.join(basedir, '.databaseFiles', 'devlog.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

csrf = CSRFProtect(app)
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    
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

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        session['user_id'] = user.id
        return jsonify({'message': 'Login successful'})
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful'})

@app.route('/api/user')
def get_user():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return jsonify({'email': user.email})
    return jsonify({'error': 'Not authenticated'}), 401

@app.route('/api/entries', methods=['POST'])
def create_entry():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    entry = LogEntry(
        project=data['project'],
        content=data['content'],
        developer_id=session['user_id'],
        timestamp=datetime.utcnow()
    )
    
    db.session.add(entry)
    db.session.commit()
    
    return jsonify({
        'id': entry.id,
        'project': entry.project,
        'content': entry.content,
        'timestamp': entry.timestamp.isoformat(),
        'developer': entry.developer.email
    })

@app.route('/api/entries/search', methods=['GET'])
def search_entries():
    query = LogEntry.query
    
    if 'date' in request.args:
        date = datetime.strptime(request.args['date'], '%Y-%m-%d')
        query = query.filter(db.func.date(LogEntry.timestamp) == date.date())
    
    if 'project' in request.args:
        query = query.filter(LogEntry.project.ilike(f"%{request.args['project']}%"))
    
    if 'content' in request.args:
        query = query.filter(LogEntry.content.ilike(f"%{request.args['content']}%"))
    
    entries = query.order_by(LogEntry.timestamp.desc()).all()
    
    return jsonify([{
        'id': entry.id,
        'project': entry.project,
        'content': entry.content,
        'timestamp': entry.timestamp.isoformat(),
        'developer': entry.developer.email
    } for entry in entries])

@app.route('/api/entries/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    entry = LogEntry.query.get_or_404(entry_id)
    
    if entry.developer_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(entry)
    db.session.commit()
    
    return jsonify({'message': 'Entry deleted successfully'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
