from flask import jsonify, request
from datetime import datetime
from models import LogEntry, db
from . import api
from .data_manager import DataManager
from .user_manager import UserManager
import logging

# logging setup for terminal output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# when get POST request; check auth, create new entries
@api.route('/entries', methods=['POST'])
def create_entry():
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

        # create entry 
        entry = LogEntry(
            project=DataManager.sanitize_project(data.get('project')),
            content=DataManager.sanitize_content(data.get('content')),
            timestamp=datetime.utcnow(),
            developer_tag=user.developer_tag # automatically use user's tag
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

#when get a GET request; return all projects and developers
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
