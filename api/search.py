from flask import jsonify, request
from datetime import datetime
from models import LogEntry, db
from . import api
from .data_manager import DataManager
from .user_manager import UserManager

# when a search request is received, check session then go ahead
@api.route('/entries/search', methods=['GET'])
def search_entries():
    print("\n=== SEARCH REQUEST RECEIVED ===")
    if not UserManager.check_session():
        return jsonify({'error': 'Session expired'}), 401

    try:
        query = LogEntry.query
        params_used = []

        # parameter fiddling
        if request.args.get('date'):
            date = datetime.strptime(request.args.get('date'), '%Y-%m-%d')
            query = query.filter(db.func.date(LogEntry.timestamp) == date.date())
            params_used.append(f"date: {date.date()}")
        
        if request.args.get('project'):
            project = request.args.get('project')
            query = query.filter(LogEntry.project.ilike(f"%{project}%"))
            params_used.append(f"project: {project}")
        
        if request.args.get('developer_tag'):
            dev_tag = request.args.get('developer_tag')
            query = query.filter(LogEntry.developer_tag == dev_tag)
            params_used.append(f"developer: {dev_tag}")

        #sort
        sort_field = request.args.get('sort_field', 'date')
        sort_order = request.args.get('sort_order', 'desc')
        
        if sort_field == 'project':
            query = query.order_by(
                LogEntry.project.desc() if sort_order == 'desc' 
                else LogEntry.project.asc()
            )
        else:
            query = query.order_by(
                LogEntry.timestamp.desc() if sort_order == 'desc' 
                else LogEntry.timestamp.asc()
            )

        entries = query.all()
        print(f"Search using parameters: {', '.join(params_used)}")
        print(f"Found {len(entries)} matching entries")

        return jsonify([entry.to_dict() for entry in entries])

    except Exception as e:
        print(f"ERROR in search: {str(e)}")
        return jsonify({'error': str(e)}), 400

    finally:
        print("=== SEARCH REQUEST COMPLETE ===\n")
