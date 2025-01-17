from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from models import db, User
from api import api
from config import Config
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Initialize CSRF protection
csrf = CSRFProtect()
csrf.init_app(app)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database setup
basedir = os.path.abspath(os.path.dirname(__file__))
os.makedirs('.databaseFiles', exist_ok=True)
db_path = os.path.join(basedir, '.databaseFiles', 'devlog.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# CSRF Configuration
app.config['WTF_CSRF_CHECK_DEFAULT'] = False
app.config['WTF_CSRF_HEADERS'] = ['X-CSRF-TOKEN']

db.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(entries_bp)

@app.after_request
def add_security_headers(response):
    for key, value in Config.CSP.items():
        response.headers[f'Content-Security-Policy'] = '; '.join(f"{k} {v}" for k, v in Config.CSP.items())
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

def check_auth():
    return 'user_id' in session

@app.route('/')
def index():
    if not check_auth():
        return redirect(url_for('login'))
    return render_template('index.html')



@app.route('/login')
def login():
    if check_auth():
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/search')
def search():
    if not check_auth():
        return redirect(url_for('login'))
def search():
    if not check_auth():
        return redirect(url_for('login'))
    return render_template('search.html')

@app.route('/signup')
def signup():
    if check_auth():
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.before_request
def log_request():
    print(f"Request: {request.method} {request.path}")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
