import re
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def validate_signup_data(data):
    errors = []
    if not data.get('email'):
        errors.append('Email is required.')
    if not data.get('password'):
        errors.append('Password is required.')
    else:
        password = data['password']
        if len(password) < 9:
            errors.append('Password must be at least 9 characters long.')
        if not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter.')
        if not re.search(r'[0-9]', password):
            errors.append('Password must contain at least one number.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append('Password must contain at least one special character.')
    return errors

def validate_login_data(data):
    errors = []
    if not data.get('email'):
        errors.append('Email is required.')
    if not data.get('password'):
        errors.append('Password is required.')
    return errors

def validate_entry_data(data):
    errors = []
    if not data.get('project'):
        errors.append('Project is required.')
    if not data.get('content'):
        errors.append('Content is required.')
    return errors

def sanitize_entry_data(data):
    sanitized_data = {
        'project': re.sub(r'[^a-zA-Z0-9-_]', '', data['project']),
        'content': data['content']
    }
    logger.debug('sanitized entry data: %s', sanitized_data)
    return sanitized_data

#read the method names lol