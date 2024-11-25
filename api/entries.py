from flask import jsonify, request, session
from models import LogEntry, db
from . import api

@api.route('/entries', methods=['POST'])
def create_entry():
    try:
        data = request.get_json()
        if not data or 'project' not in data or 'content' not in data:
            return jsonify({'error': 'Missing required fields'}), 400

        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        entry = LogEntry(
            project=data['project'],
            content=data['content'],
            developer_tag=user.developer_tag
        )

        db.session.add(entry)
        db.session.commit()

        return jsonify({'message': 'Entry created successfully', 'entry': entry.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400