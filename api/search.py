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
    logger.info("Search request received")
    
    if not UserManager.check_session():
        logger.warning("Unauthorized search attempt")
        return jsonify({'error': 'Authentication required'}), 401
    
    # if no search parameters are provided, tell error
    if not any([
    request.args.get('project'),
    request.args.get('developer_tag'),
    request.args.get('date')
    ]):
        return jsonify({'error': 'Please enter at least one search parameter'}), 400

    try:
        query = LogEntry.query
        search_params = []

        # Date filter using timestamp
        date = request.args.get('date')
        if date:
            search_date = datetime.strptime(date, '%Y-%m-%d')
            query = query.filter(db.func.date(LogEntry.timestamp) == search_date.date())
            search_params.append(f"date: {date}")

        # project filter (only apply if true)
        project = request.args.get('project', '')
        if project:
            project = DataManager.sanitize_project(project)
            query = query.filter(LogEntry.project.ilike(f"%{project}%"))
            search_params.append(f"project: {project}")

        # developer filter (only apply if true)
        developer = request.args.get('developer_tag', '')
        if developer:
            developer = DataManager.sanitize_developer_tag(developer)
            query = query.filter(LogEntry.developer_tag.ilike(f"%{developer}%"))
            search_params.append(f"developer: {developer}")

        # sort
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
        logger.info(f"Search completed with params: {', '.join(search_params)}")
        logger.info(f"Found {len(entries)} matching entries")

        return jsonify([entry.to_dict() for entry in entries])

    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({'error': str(e)}), 400
