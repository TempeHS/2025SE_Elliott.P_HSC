from flask import jsonify, request
from datetime import datetime
from models import LogEntry, db
from . import api
from .data_manager import DataManager
from .user_manager import UserManager
import logging

logger = logging.getLogger(__name__)

@api.route('/entries/search', methods=['GET'])
def search_entries():
    print("\n=== SEARCH REQUEST RECEIVED ===")
    
    if not UserManager.check_session():
        print("ERROR: Unauthorized search attempt")
        return jsonify({'error': 'Authentication required'}), 401

    try:
        query = LogEntry.query
        search_params = []

        project = request.args.get('project', '')
        if project:
            project = DataManager.sanitize_project(project)
            query = query.filter(LogEntry.project.ilike(f"%{project}%"))
            search_params.append(f"project: {project}")

        developer = request.args.get('developer_tag', '')
        if developer:
            developer = DataManager.sanitize_developer_tag(developer)
            query = query.filter(LogEntry.developer_tag.ilike(f"%{developer}%"))
            search_params.append(f"developer: {developer}")

        date = request.args.get('date')
        if date:
            search_date = datetime.strptime(date, '%Y-%m-%d')
            query = query.filter(db.func.date(LogEntry.start_time) == search_date.date())
            search_params.append(f"date: {date}")

        entries = query.order_by(LogEntry.start_time.desc()).all()
        print(f"Found {len(entries)} matching entries")
        print(f"Search parameters: {', '.join(search_params)}")
        
        return jsonify([entry.to_dict() for entry in entries])

    except Exception as e:
        print(f"ERROR during search: {str(e)}")
        return jsonify({'error': str(e)}), 400

    finally:
        print("=== SEARCH REQUEST COMPLETE ===\n")
