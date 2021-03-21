gunicorn --capture-output --bind 0.0.0.0:8000 --access-logfile - snake_eyes.app:create_app()
