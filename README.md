# Prowler Scanner API (Django REST + Celery + Redis)

A Django REST API to manage asynchronous Prowler scans, track their real-time status, and store scan results — ready for production integration.

---

## Features

- **Scans**: Create, list, update, delete scans. An async run via Celery tasks
- **Scan Status**: Real-time scan status at `/api/scans/<id>/status/`
- **Checks** & **Findings** CRUD endpoints
- Swagger API docs: `/swagger/`
- Built-in support for async task management with Redis and Celery
- Safe parallel task execution with locking
- Singleton Redis provider for efficiency
- Ready for scaling and production hardening

---

## Stack

- Python 3.11
- Django 4.2 LTS
- Django REST Framework
- Celery 5.x
- Redis 5.x
- drf-yasg (Swagger UI)
- SQLite3 (default, easy to switch to Postgres)

---

## Setup

```bash
# 1. Clone repo
git clone https://github.com/krishnx/prowler.git
cd prowler_scanner

# 2. Python env
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. DB migrate
python manage.py migrate

# 4. Start Redis (ensure port matches REDIS_PORT env or RedisProvider)
run on custom port:
redis-server --port 6380

# 5. Start Django
python manage.py runserver

# 6. Start Celery worker
celery -A prowler_scanner worker --loglevel=info
```
---

## Make commands
```bash
# 1. Run make migrate once before first run to set up DB.
make migrate

# 2. Run make redis to start Redis (if installed locally).
make redis-server

# 3. Run make celery to start the Celery worker.
make celery

# 4. Run make runserver to launch the Django server.
make runserver

5. Run make clean to clean up Python cache files.
make clean
```
