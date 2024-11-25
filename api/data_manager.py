class DataManager:
    @staticmethod
    def sanitize_email(email):
        return email.strip().lower()

    @staticmethod
    def sanitize_developer_tag(developer_tag):
        return developer_tag.strip().lower()