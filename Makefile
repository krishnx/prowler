.PHONY: help runserver migrate celery redis clean

help:
	@echo "Usage:"
	@echo "  make runserver    # Run Django development server"
	@echo "  make migrate      # Apply Django migrations"
	@echo "  make celery       # Start Celery worker"
	@echo "  make redis        # Start Redis server (assuming redis-server is installed)"
	@echo "  make clean        # Remove __pycache__ and .pyc files"

runserver:
	python manage.py runserver

migrate:
	python manage.py migrate

celery:
	celery -A prowler_project worker --loglevel=info

redis:
	redis-server

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
