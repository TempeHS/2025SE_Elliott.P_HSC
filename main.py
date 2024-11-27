import os
from flask import Flask, render_template, session, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from api.auth import auth_bp
from api.entries import entries_bp
from models import db
from logger_config import logger

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Database setup
basedir = os.path.abspath(os.path.dirname(__file__))
os.makedirs(os.path.join(basedir, '.databaseFiles'), exist_ok=True)
db_path = os.path.join(basedir, '.databaseFiles', 'devlog.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

csrf = CSRFProtect(app)
db.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(entries_bp)

@app.before_request
def log_request_info():
    logger.debug(f'Accessed route: {request.path}')
    if request.method == 'POST':
        logger.debug(f'POST data: {request.get_json()}')

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login_page'))
    return render_template('index.html')

@app.route('/search')
def search_page():
    if 'user_id' not in session:
        return redirect(url_for('auth.login_page'))
    return render_template('search.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)