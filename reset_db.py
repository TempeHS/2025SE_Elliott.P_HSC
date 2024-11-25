from main import app, db
from models import User, LogEntry

def reset_database():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("Dropped all tables.")

        # Recreate all tables
        db.create_all()
        print("Recreated all tables.")

        # Optionally, you can add some initial data here
        # Example:
        # user = User(email='admin@example.com', developer_tag='admin')
        # user.set_password('adminpassword')
        # db.session.add(user)
        # db.session.commit()
        # print("Added initial data.")

if __name__ == '__main__':
    reset_database()