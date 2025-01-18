from flask import Blueprint, request, jsonify, session
from models import db, LogEntry, User
from datetime import datetime
from api.data_management import sanitize_entry_data, validate_entry_data
from logger_config import logger
from flask import jsonify, request
from datetime import datetime
from models import LogEntry, db
from . import api
from .data_manager import DataManager
from .user_manager import UserManager
import logging

# Configure logging to output to terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

entries_bp = Blueprint('entries', __name__)

@entries_bp.route('/api/entries', methods=['POST'])
def create_entry():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    logger.debug('create entry data: %s', data)
    errors = validate_entry_data(data)
    if errors:
        logger.debug('create entry errors: %s', errors)
        return jsonify({'error': errors}), 400

    sanitized_data = sanitize_entry_data(data)
    entry = LogEntry(
        project=sanitized_data['project'],
        content=sanitized_data['content'],
        developer_id=session['user_id']
    )
    db.session.add(entry)
    db.session.commit()
    logger.debug('entry created: %s', entry)
    return jsonify({
        'id': entry.id,
        'project': entry.project,
        'content': entry.content,
        'timestamp': entry.timestamp,
        'developer': entry.developer.email
    })

@entries_bp.route('/api/projects', methods=['GET'])
def get_projects():
    projects = db.session.query(LogEntry.project).distinct().all()
    project_list = [project[0] for project in projects]
    logger.debug('projects retrieved: %s', project_list)
    return jsonify(project_list)

@entries_bp.route('/api/projects', methods=['POST'])
def create_project():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    project_name = data.get('project')
    if not project_name:
        return jsonify({'error': 'Project name is required'}), 400

    existing_project = db.session.query(LogEntry.project).filter_by(project=project_name).first()
    if existing_project:
        return jsonify({'error': 'Project already exists'}), 400

    logger.debug('project created: %s', project_name)
    return jsonify({'message': 'Project created', 'project': project_name})

@entries_bp.route('/api/entries/search', methods=['GET'])
def search_entries():
    project = request.args.get('project')
    date = request.args.get('date')
    content = request.args.get('content')
    filter_by = request.args.get('filter')
    sort_order = request.args.get('sort', 'asc')

    logger.debug('search entries query: project=%s, date=%s, content=%s, filter=%s, sort=%s', project, date, content, filter_by, sort_order)

    query = LogEntry.query

    if project:
        query = query.filter(LogEntry.project == project)
    if date:
        query = query.filter(db.func.date(LogEntry.timestamp) == date)
    if content:
        query = query.filter(LogEntry.content.contains(content))

    if filter_by == 'project':
        query = query.order_by(LogEntry.project)
    elif filter_by == 'content':
        query = query.order_by(LogEntry.content)

    if sort_order == 'asc':
        query = query.order_by(LogEntry.timestamp.asc())
    else:
        query = query.order_by(LogEntry.timestamp.desc())

    entries = query.all()

    results = [{
        'id': entry.id,
        'project': entry.project,
        'content': entry.content,
        'timestamp': entry.timestamp,
        'developer': entry.developer.email
    } for entry in entries]

    logger.debug('search entries results: %s', results)
    return jsonify(results)

@entries_bp.route('/api/entries/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    entry = LogEntry.query.get(entry_id)
    if not entry:
        return jsonify({'error': 'Entry not found'}), 404

    if entry.developer_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(entry)
    db.session.commit()
    logger.debug('entry deleted: %s', entry)
    return jsonify({'message': 'Entry deleted'})
#does the method names
#also handles input snaitization and validation forwarding to the data_management.py file

    print("\n=== NEW ENTRY CREATION ATTEMPT ===")
    
    user = UserManager.get_current_user()
    if not user:
        print("ERROR: No authenticated user found")
        return jsonify({'error': 'Authentication required'}), 401

    try:
        data = request.get_json()
        if not data:
            print("ERROR: No JSON data in request")
            return jsonify({'error': 'No data provided'}), 400

        # Create entry with current user's developer tag
        entry = LogEntry(
            project=DataManager.sanitize_project(data.get('project')),
            content=DataManager.sanitize_content(data.get('content')),
            timestamp=datetime.utcnow(),
            developer_tag=user.developer_tag  # Automatically use authenticated user's tag
        )

        print(f"Creating entry for project '{entry.project}' by {entry.developer_tag}")
        
        db.session.add(entry)
        db.session.commit()
        
        print(f"SUCCESS: Entry created with ID: {entry.id}")
        return jsonify({
            'status': 'success',
            'message': 'Entry created successfully',
            'entry': entry.to_dict()
        }), 201

    except Exception as e:
        print(f"ERROR during entry creation: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        print("=== ENTRY CREATION ATTEMPT COMPLETE ===\n")

@api.route('/entries/metadata', methods=['GET'])
def get_metadata():
    print("\n=== FETCHING METADATA ===")
    try:
        # Get unique projects
        projects = db.session.query(LogEntry.project).distinct().all()
        project_list = sorted([project[0] for project in projects])
        
        # Get unique developers
        developers = db.session.query(LogEntry.developer_tag).distinct().all()
        developer_list = sorted([dev[0] for dev in developers])
        
        print(f"Found {len(project_list)} projects and {len(developer_list)} developers")
        
        return jsonify({
            'projects': project_list,
            'developers': developer_list
        })
        
    except Exception as e:
        print(f"ERROR fetching metadata: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
    finally:
        print("=== METADATA FETCH COMPLETE ===\n")
