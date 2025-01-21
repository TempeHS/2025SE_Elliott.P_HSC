<<<<<<< HEAD
import os
from flask import Flask, render_template, session, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from api.auth import auth_bp
from api.entries import entries_bp
from models import db
from logger_config import logger
=======
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
import logging
from models import db, User
from api import api
import os
>>>>>>> fork/main

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
<<<<<<< HEAD
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
=======

# Initialize CSRF protection
csrf = CSRFProtect()
csrf.init_app(app)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
>>>>>>> fork/main

# Database setup
basedir = os.path.abspath(os.path.dirname(__file__))
os.makedirs(os.path.join(basedir, '.databaseFiles'), exist_ok=True)
db_path = os.path.join(basedir, '.databaseFiles', 'devlog.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

<<<<<<< HEAD
csrf = CSRFProtect(app)
=======
# CSRF Configuration
app.config['WTF_CSRF_CHECK_DEFAULT'] = False
app.config['WTF_CSRF_HEADERS'] = ['X-CSRF-TOKEN']

>>>>>>> fork/main
db.init_app(app)

<<<<<<< HEAD
app.register_blueprint(auth_bp)
app.register_blueprint(entries_bp)

@app.before_request
def log_request_info():
    logger.debug(f'Accessed route: {request.path}')
    if request.method == 'POST':
        logger.debug(f'POST data: {request.get_json()}')
=======
print("Available routes:", [str(rule) for rule in app.url_map.iter_rules()])

def check_auth():
    return 'user_id' in session
>>>>>>> fork/main

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login_page'))
    return render_template('index.html')

<<<<<<< HEAD
@app.route('/search')
def search_page():
    if 'user_id' not in session:
        return redirect(url_for('auth.login_page'))
    return render_template('search.html')
=======
@app.route('/signup')
def signup():
    return render_template('signup.html', hide_nav=True)

@app.route('/login')
def login():
    return render_template('login.html', hide_nav=True)

@app.route('/search')
def search():
    if not check_auth():
        return redirect(url_for('login'))
    return render_template('search.html')

@app.before_request
def log_request():
    logger.info(f"Request: {request.method} {request.path}")
    if request.is_json:
        logger.info(f"JSON Data: {request.get_json()}")

@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"Error occurred: {str(error)}", exc_info=True)
    return jsonify({'error': str(error)}), 500

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
>>>>>>> fork/main


@app.route('/privacy')
def privacy():
    if not check_auth():
        return redirect(url_for('login'))
    return render_template('privacy.html')

#HAVE THIS AT THE END!!!!
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

#the render pipeline and redirectionfile