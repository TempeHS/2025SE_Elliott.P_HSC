from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
import logging
from models import db, User
from api import api
import os
from config import Config
from flask_mail import Mail

# configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config.from_object(Config)

# initialize mail
mail = Mail()
mail.init_app(app)

# initialize CSRF protection
csrf = CSRFProtect()
csrf.init_app(app)

# initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# database setup
basedir = os.path.abspath(os.path.dirname(__file__))
os.makedirs('.databaseFiles', exist_ok=True)
db_path = os.path.join(basedir, '.databaseFiles', 'devlog.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# CSRF Configuration
app.config['WTF_CSRF_CHECK_DEFAULT'] = False
app.config['WTF_CSRF_HEADERS'] = ['X-CSRF-TOKEN']

db.init_app(app)
app.register_blueprint(api, url_prefix='/api')

print("Available routes:", [str(rule) for rule in app.url_map.iter_rules()])

# more logging
@app.before_request
def log_request():
    logger.info(f"Request: {request.method} {request.path}")
    if request.is_json and request.get_data():
        try:
            logger.info(f"JSON Data: {request.get_json()}")
        except:
            pass

def check_auth():
    return 'user_id' in session

@app.route('/')
def index():
    if not check_auth():
        return redirect(url_for('login'))
    return render_template('index.html')

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


@app.route('/privacy')
def privacy():
    if not check_auth():
        return redirect(url_for('login'))
    return render_template('privacy.html')

@app.route('/home')
def home():
    if not check_auth():
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/entry/<int:entry_id>')
def view_entry(entry_id):
    if not check_auth():
        return redirect(url_for('login'))
    return render_template('entry_veiw.html')

@app.route('/profile')
def profile():
    if not check_auth():
        return redirect(url_for('login'))
    return render_template('profile.html')


#HAVE THIS AT THE END!!!!
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 
    #turn to True for logs