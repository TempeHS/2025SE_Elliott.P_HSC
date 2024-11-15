from flask import jsonify, request
from datetime import datetime
from models import LogEntry, db
from . import api

@api.route('/entries/search', methods=['GET'])
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
