from flask import jsonify, request, session
from datetime import datetime
from models import db, LogEntry
from . import api

@api.route('/entries', methods=['POST'])
def create_entry():
    if 'user_id' not in session:
        print(f"unauthorized: {request.remote_addr}")
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        print(f"new entry by user {session['user_id']}")
        
        entry = LogEntry(
            project=data['project'],
            content=data['content'],
            developer_id=session['user_id'],
            timestamp=datetime.utcnow()
        )
        
        db.session.add(entry)
        db.session.commit()
        print(f"entry created: {entry.project}")
        
        return jsonify({
            'id': entry.id,
            'project': entry.project,
            'content': entry.content,
            'timestamp': entry.timestamp.isoformat(),
            'developer': entry.developer.email
        })
    except Exception as e:
        print(f"entry error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create entry'}), 500

