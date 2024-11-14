from flask import jsonify, request
from flask_login import login_required, current_user
from datetime import datetime

@login_required
def get_user():
    user_data = {
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'created_at': datetime.utcnow().isoformat()
    }
    return jsonify(user_data), 200

@login_required
def update_user():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    allowed_fields = ['username', 'email']
    updates = {k: v for k, v in data.items() if k in allowed_fields}
    
    try:
        for key, value in updates.items():
            setattr(current_user, key, value)
        db.session.commit()
        return jsonify({'message': 'User updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
