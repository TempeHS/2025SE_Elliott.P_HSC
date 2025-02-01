# DevLog - Developer Log Management System

### IF THE MAIL DOESNT WORK, PLEASE MESSAGE ME ON elliott.pezzutti@education.nsw.gov.au

### I tried to change the commit messages, but the source control was being weird, so I just kept the changes in commit_message_change.txt will try to fix at school before due date

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

1. set up dependancies:

  pip install -r requirements.txt

4. verify .env file:

  SECRET_KEY=your-secure-secret-key-here
  DATABASE_URL=sqlite:///.databaseFiles/devlog.db
  MAIL_USERNAME=elliottpezzutti@gmail.com
  MAIL_PASSWORD=itoy hsyh kudx cgsf 

the mail password is a app password generated from my google account, mail me if it does not work and needs to be updated





## generate base test data
You can create whatever test data you want, but here is a basic example:
ALSO THE API ENDPOINT VERSION OF THIS IS POSSIBLY FASTER, but fidgety

1. Create User 1:
go to sign up and use
```
      email: user1@example.com
      password: UserUser!1
      developer_tag: user1
```

2. Create User 2:
go to sign up and use
```
      email: user2@example.com
      password: UserUser@2
      developer_tag: user2
```
3. generate API key:
you can do this from the user profile page, by clicking the generate API key button
this can be done with API, but its just easier and more functional to do it from the profile page.

4. generate entries, FILL IN API KEY:
```bash
      project: Project Name,
      content: "Entry content,
      repository_url: https://github.com/user/repo
      start_time: 2024-01-31T10:00:00
      end_time: 2024-01-31T11:00:00
```


<details>
<summary> API usage test with enpoints (works) </summary>

1. Create User 1:
or API it
```bash
  curl -X POST http://localhost:5000/api/auth/signup \
    -H "Content-Type: application/json" \
    -d '{
      "email": "user1@example.com",
      "password": "UserUser!1",
      "developer_tag": "user1"
    }'
```
2. Create User 2:
or API it
```bash
  curl -X POST http://localhost:5000/api/auth/signup \
    -H "Content-Type: application/json" \
    -d '{
      "email": "user2@example.com",
      "password": "UserUser@2",
      "developer_tag": "user2"
    }'
```
3. generate API key:
you can do this from the user profile page, by clicking the generate API key button
this can be done with API, but its just easier and more functional to do it from the profile page.

4. generate entries, FILL IN API KEY:
```bash
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
```
</details>

### User Acceptance Testing Guide

1. Sign in with one of the example credintials (in this case user1) and Create a new entry with alot of text for the content

2. then go to your profile page and check that the entry is there, then click on it and it will go to the full veiw

3. then create another entry with a different project and check that it is there and verify the statistics on the profile page match the entries

4. go to the profile page, click log out, sign in on another user(user2), and enter a different entry under one of the same project names of the other user.

5. log out, sign in as the first user(user1) and check the home page to see that the entry matching your project activity is there.

<details>
<summary>if you want to API this</summary>

# this is the api version of the above, but it doesnt demonstrate the funcitonality of the website well
## Get CSRF token
```bash
curl -s http://localhost:5000/login | grep "csrf-token"
```
## 1. Sign in as user1 and create entry FILL IN CSRF
```bash
curl -X POST http://localhost:5000/api/auth/login -c cookies.txt -H "Content-Type: application/json" -H "X-CSRF-TOKEN: YOUR_TOKEN" -d '{"email":"user1@example.com", "password":"UserUser!1"}'

curl -X POST http://localhost:5000/api/entries -b cookies.txt -H "Content-Type: application/json" -H "X-CSRF-TOKEN: YOUR_TOKEN" -d '{
    "project": "project_alpha",
    "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    "repository_url": "https://github.com/test/project_alpha",
    "start_time": "2024-02-01T09:00:00",
    "end_time": "2024-02-01T11:30:00"
}'
```
## 2. Check profile and entry
```bash
curl -b cookies.txt http://localhost:5000/api/entries/user-stats
curl -b cookies.txt http://localhost:5000/api/entries/1
```
## 3. Create second entry and verify stats FILL IN CSRF
```bash
curl -X POST http://localhost:5000/api/entries -b cookies.txt -H "Content-Type: application/json" -H "X-CSRF-TOKEN: YOUR_TOKEN" -d '{
    "project": "project_beta",
    "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    "repository_url": "https://github.com/test/project_beta",
    "start_time": "2024-02-01T13:00:00",
    "end_time": "2024-02-01T15:30:00"
}'

curl -b cookies.txt http://localhost:5000/api/entries/user-stats
```
## 4. Logout, login as user2, create entry FILL IN CSRF
```bash
curl -X POST http://localhost:5000/api/auth/logout -b cookies.txt -H "X-CSRF-TOKEN: YOUR_TOKEN"

curl -X POST http://localhost:5000/api/auth/login -c cookies.txt -H "Content-Type: application/json" -H "X-CSRF-TOKEN: YOUR_TOKEN" -d '{"email":"user2@example.com", "password":"UserUser@2"}'

curl -X POST http://localhost:5000/api/entries -b cookies.txt -H "Content-Type: application/json" -H "X-CSRF-TOKEN: YOUR_TOKEN" -d '{
    "project": "project_alpha",
    "content": "User2 working on project_alpha. Adding new features to existing codebase.",
    "repository_url": "https://github.com/test/project_alpha",
    "start_time": "2024-02-01T16:00:00",
    "end_time": "2024-02-01T17:30:00"
}'
```
## 5. Logout, login as user1, check home
```bash
curl -X POST http://localhost:5000/api/auth/logout -b cookies.txt -H "X-CSRF-TOKEN: YOUR_TOKEN"

curl -X POST http://localhost:5000/api/auth/login -c cookies.txt -H "Content-Type: application/json" -H "X-CSRF-TOKEN: YOUR_TOKEN" -d '{"email":"user1@example.com", "password":"UserUser!1"}'

curl -b cookies.txt http://localhost:5000/api/entries/search?project=project_alpha
```
^ this doesnt demonstrate the functionality of the home page correctly, but pretty much it does
</details>

##### If all tests are passed, log entry, home page, profile page, and cross user entry meta data should be working correctly.


#### if you ever have any issues PLEASE WRITE THEM DOWN IN A .TXT FILE and COPY AND PASTE THE LOGS / ERROR ALERTS INTO THE FILE.



## FUNCTIONAL API ENDPOINTS

this doesnt have alot of support, but it is usable

## Get CSRF token needed for alot of the commands
### Save CSRF token to file
```bash
curl -s http://localhost:5000/login | grep "csrf-token" | sed 's/.*content="\([^"]*\)".*/\1/' > csrf_token.txt
```

#### Function to read token (add to start of script)

```bash
TOKEN=$(cat csrf_token.txt) &&
```

## authentication stuff


<details>
<summary> 
Login as a user with 2fa disabled
</summary>

fill in the YOUR_EMAIL, and USER_PASSWORD
```bash
TOKEN=$(cat csrf_token.txt) &&
curl -X POST http://localhost:5000/api/auth/login -c cookies.txt -H "Content-Type: application/json" -H "X-CSRF-TOKEN: $TOKEN" -d '{
    "email": "user1@example.com",
    "password": "UserUser!1"
}'
```
you will then be logged in for a bit
</details>

<details>
<summary> Login as a user with 2fa enabled (no api key)</summary>

1. fill in the  YOUR_EMAIL, and USER_PASSWORD
```bash
TOKEN=$(cat csrf_token.txt) &&
curl -X POST http://localhost:5000/api/auth/login -c cookies.txt -H "Content-Type: application/json" -H "X-CSRF-TOKEN: $TOKEN" -d '{
    "email": "YOUR_EMAIL",
    "password": "USER_PASSWORD"
}'
```

2. fill in the VERIFICATION (code sent to your email)
```bash
TOKEN=$(cat csrf_token.txt) &&
curl -X POST http://localhost:5000/api/auth/verify-login -b cookies.txt -H "Content-Type: application/json" -H "X-CSRF-TOKEN: $TOKEN" -d '{
    "code": "VERIFICATION"
}'
```

you will now be logged in with 2fa for a bit

</details>

### logout
TOKEN=$(cat csrf_token.txt) &&
curl -X POST http://localhost:5000/api/auth/logout -b cookies.txt -H "X-CSRF-TOKEN: $TOKEN"

## entry stuff

###
<details>
<summary> create entries once logged in</summary>


1. log in

2. fill in this template
```bash
TOKEN=$(cat csrf_token.txt) &&
curl -X POST http://localhost:5000/api/entries -b cookies.txt -H "Content-Type: application/json" -H "X-CSRF-TOKEN: $TOKEN" -d '{
    "project": "project_name",
    "content": "Entry content here",
    "repository_url": "https://github.com/user/repo",
    "start_time": "2024-02-01T09:00:00",
    "end_time": "2024-02-01T10:30:00"
}'
```
</details>

<details>
<summary> search entries</summary>


### get some general metadata
```bash
curl -b cookies.txt http://localhost:5000/api/entries/metadata
```
### Get All Entries
```bash
curl -b cookies.txt http://localhost:5000/api/entries
```
### Get Single Entry
```bash
curl -b cookies.txt http://localhost:5000/api/entries/1
```
### Search Entries
```bash
curl -b cookies.txt "http://localhost:5000/api/entries/search?project=project_name&developer_tag=dev1&date=2024-02-01"
```
</details>

<details>
<summary> profile utils</summary>


### Enable 2FA
```bash
TOKEN=$(cat csrf_token.txt) &&
curl -X POST http://localhost:5000/api/auth/enable-2fa -b cookies.txt -H "Content-Type: application/json" -H "X-CSRF-TOKEN: $TOKEN"
```
### Verify 2FA Setup
```bash 
TOKEN=$(cat csrf_token.txt) &&
curl -X POST http://localhost:5000/api/auth/verify-2fa -b cookies.txt -H "Content-Type: application/json" -H "X-CSRF-TOKEN: $TOKEN" -d '{
    "code": "123456"
}'
```

### Disable 2FA
```bash
TOKEN=$(cat csrf_token.txt) &&
curl -X POST http://localhost:5000/api/auth/disable-2fa -b cookies.txt -H "Content-Type: application/json" -H "X-CSRF-TOKEN: $TOKEN"
```
</details>