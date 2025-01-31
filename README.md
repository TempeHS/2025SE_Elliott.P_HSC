# DevLog - Developer Log Management System

## Security Features
- Bcrypt password hashing
- CSRF protection on all forms
- Session management with 1-hour timeout
- Two-Factor Authentication via email
- API key authentication
- Input sanitization and validation
- Secure cookie handling
- XSS protection

## API Endpoints

### Authentication
- POST /api/auth/signup     - Create new user
- POST /api/auth/login      - Login existing user
- POST /api/user/generate-key - Generate API key
- POST /api/auth/enable-2fa - Enable 2FA
- POST /api/auth/verify-2fa - Verify 2FA code

### Entries
- POST /api/entries         - Create new entry
- GET  /api/entries        - Get all entries
- GET  /api/entries/search - Search entries with filters
- GET  /api/entries/metadata - Get projects and developers list

# Devlog webapp initialisation and User Acceptance Testing

## Initialisation
Prerequisites:
- Python 3.12+
- Flask 3.0.0+
- SQLite 3+
(we have this because of codespace)

1. set up dependancies

  pip install -r requirements.txt

2. create venv

  python -m venv venv

3. verify .env file

  SECRET_KEY=your-secure-secret-key-here
  DATABASE_URL=sqlite:///.databaseFiles/devlog.db
  MAIL_USERNAME=elliottpezzutti@gmail.com
  MAIL_PASSWORD=itoy hsyh kudx cgsf 

the mail password is a app password generated from google account settings





## API Usage Example
1. Create User 1

  curl -X POST http://localhost:5000/api/auth/signup \
    -H "Content-Type: application/json" \
    -d '{
      "email": "user1@example.com",
      "password": "SecurePass123!",
      "developer_tag": "Frontend"
    }'

2. Create User 2

  curl -X POST http://localhost:5000/api/auth/signup \
    -H "Content-Type: application/json" \
    -d '{
      "email": "user2@example.com",
      "password": "TestPass456!",
      "developer_tag": "Backend"
    }'

3. generate entries, FILL IN API KEY

  curl -X POST http://your-api/api/entries \
    -H "X-API-Key: YOUR_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "project": "Project Name",
      "content": "Entry content",
      "repository_url": "https://github.com/user/repo",
      "start_time": "2024-01-31T10:00:00",
      "end_time": "2024-01-31T11:00:00"
    }'

User Acceptance Testing Guide
1. Create Test Users

User 1:

    Email: user1@gmail.com
    Password: Useruser!1
    Developer Tag: user1

User 2:

    Email: user2@gmail.com
    Password: Useruser!2
    Developer Tag: user2

2FA Test:

    Use your personal email to test 2FA functionality
    Then enable 2fa on the profile page, and check your email (and junk, the email comes from newmonkeyooohahhhh@gmail.com) and then log out and sign in to 2FAuthenticate

## 2. Testing Steps

    Create entries using the API endpoint
    Test search functionality with different filters
    Try sorting entries by date and project
    View full entry details
    Test validation:
        Try creating entries with end time before start time
        Attempt signup with invalid password formats
        Test input sanitization with special characters
