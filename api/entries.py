from flask import jsonify, request, session
from datetime import datetime
from models import db, LogEntry
from . import api

@api.route('/entries', methods=['POST'])
def create_entry():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    entry = LogEntry(
        project=data['project'],
        content=data['content'],
        developer_id=session['user_id'],
        timestamp=datetime.utcnow()
    )
    
    db.session.add(entry)
    db.session.commit()
    
    return jsonify({
        'id': entry.id,
        'project': entry.project,
        'content': entry.content,
        'timestamp': entry.timestamp.isoformat(),
        'developer': entry.developer.email
    })

@api.route('/entries/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    entry = LogEntry.query.get_or_404(entry_id)
    
    if entry.developer_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(entry)
    db.session.commit()
    
    return jsonify({'message': 'Entry deleted successfully'})
