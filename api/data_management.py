import re
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def validate_signup_data(data):
    errors = []
    if not data.get('email'):
        errors.append('email is required.')
    if not data.get('password'):
        errors.append('password is required.')
    return errors

def validate_login_data(data):
    errors = []
    if not data.get('email'):
        errors.append('email is required.')
    if not data.get('password'):
        errors.append('password is required.')
    return errors

def validate_entry_data(data):
    errors = []
    if not data.get('project'):
        errors.append('project is required.')
    if not data.get('content'):
        errors.append('content is required.')
    return errors

def sanitize_entry_data(data):
    sanitized_data = {
        'project': re.sub(r'[^a-zA-Z0-9-_]', '', data['project']),
        'content': data['content']
    }
    logger.debug('sanitized entry data: %s', sanitized_data)
    return sanitized_data