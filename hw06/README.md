# hasker app
django app with some functionality of stackoverflow

## how to run
1. get this project from git
2. make .env file in hasker folder
```
SECRET_KEY = 'your_secret_key'
HOST = 'gunicorn'
DEBUG = True

POSTGRES_HOST = 'db'
POSTGRES_NAME = postgres
POSTGRES_USER = postgres
POSTGRES_PASSWORD = postgres
```
3. docker compose build
4. docker compose up -d
5. go to hasker page in browser by your ip