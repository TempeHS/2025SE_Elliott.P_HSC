import os
from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from models import db
from api import api

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Database setup
basedir = os.path.abspath(os.path.dirname(__file__))
os.makedirs('.databaseFiles', exist_ok=True)
db_path = os.path.join(basedir, '.databaseFiles', 'devlog.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Security setup
csrf = CSRFProtect(app)
db.init_app(app)
app.register_blueprint(api, url_prefix='/api')

def check_auth():
    return 'user_id' in session

@app.route('/')
def index():
    print("index accessed")
    if not check_auth():
        print("auth needed -> login")
        return redirect('/login')
    print("serving index")
    return render_template('index.html')

@app.route('/login')
def login():
    print("login accessed")
    if check_auth():
        print("already auth -> index")
        return redirect('/')
    print("serving login")
    return render_template('login.html')

@app.route('/signup')
def signup():
    print("signup accessed")
    if check_auth():
        print("already auth -> index")
        return redirect('/')
    print("serving signup")
    return render_template('signup.html')

@app.before_request
def log_request():
    print(f"req: {request.method} {request.url} from {request.remote_addr}")

if __name__ == '__main__':
    with app.app_context():
        print("init db...")
        db.create_all()
        print("db ready")
    app.run(debug=True)