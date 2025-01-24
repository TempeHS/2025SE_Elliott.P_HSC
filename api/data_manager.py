import re
from datetime import datetime

class DataManager:
    
    
    # <sanitize stuff start-------!>
    
    @staticmethod
    def sanitize_repository_url(url):
        if not url:
            return None
        url = url.strip()
        # Simple URL pattern check
        url_pattern = r'^https?:\/\/(github\.com|gitlab\.com|bitbucket\.org)\/[\w\-\.\/]+$'
        if not re.match(url_pattern, url):
            raise ValueError("URL must be a valid repository URL")
        return url

    
    @staticmethod
    def validate_timestamps(start_time, end_time):
        try:
            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(end_time)
            if end <= start:
                raise ValueError("End time must be after start time")
            return start, end
        except ValueError as e:
            raise ValueError(f"Invalid timestamp format: {str(e)}")

    @staticmethod
    def calculate_time_worked(start_time, end_time):
        diff_minutes = (end_time - start_time).total_seconds() / 60
        return round(diff_minutes / 15) * 15

    @staticmethod
    def sanitize_email(email):
        return email.strip().lower()

    @staticmethod
    def sanitize_developer_tag(developer_tag):
        return developer_tag.strip().lower()
        
    @staticmethod
    def sanitize_project(project):
        if not project or not isinstance(project, str):
            raise ValueError("Invalid project name")
        project = project.strip()
        if len(project) > 100:
            raise ValueError("Project name must be less than 100 characters")
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9\s_-]*$', project):
            raise ValueError("Project name must start with alphanumeric and contain only letters, numbers, spaces, underscores, or hyphens")
        return project[:100]

    @staticmethod
    def sanitize_content(content):
        if not content or not isinstance(content, str):
            raise ValueError("Content cannot be empty")
        content = content.strip()
        if len(content) > 1000:  # Adding reasonable content limit
            raise ValueError("Content exceeds maximum length of 1000 characters")
        return content

    @staticmethod
    def sanitize_search_params(params):
        clean_params = {}
        if 'project' in params:
            clean_params['project'] = DataManager.sanitize_project(params['project'])
        if 'developer_tag' in params:
            clean_params['developer_tag'] = DataManager.sanitize_developer_tag(params['developer_tag'])
        if 'date' in params:
            try:
                datetime.strptime(params['date'], '%Y-%m-%d')
                clean_params['date'] = params['date']
            except ValueError:
                raise ValueError("Invalid date format")
        return clean_params


    #<sanitize stuff ------!>

        # <should probably include some validation exception handling here