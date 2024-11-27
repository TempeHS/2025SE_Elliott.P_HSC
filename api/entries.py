from flask import Blueprint, request, jsonify, session
from models import db, LogEntry, User
from datetime import datetime
from api.data_management import sanitize_entry_data, validate_entry_data
from logger_config import logger

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
    query = request.args.get('query')
    logger.debug('search entries query: %s', query)
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    entries = LogEntry.query.filter(
        (LogEntry.project.contains(query)) |
        (LogEntry.content.contains(query)) |
        (LogEntry.developer.has(email=query))
    ).all()

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