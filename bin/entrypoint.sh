#!/bin/bash


if [[ $DEPLOYMENT_PLATFORM == "heroku" ]]; then
    if [[ $APP_TYPE == "web" ]]; then
        # Do a db revision upgrade as it is idempotent
        snake_eyes db upgrade $DB_REVISION

        # Seed the db only when required
        if [[ $SEED_DB -eq 1 ]]; then
            snake_eyes add all
        fi

        # Sync stripe plans
        snake_eyes stripe sync

        gunicorn --config "python:config.gunicorn" "snake_eyes.app:create_app()"
    else
        celery worker --beat --app snake_eyes.blueprints.contact.tasks --loglevel info
    fi
elif [[ $DEPLOYMENT_PLATFORM == "local" ]]; then
    if [[ $APP_TYPE == "web" ]]; then
        gunicorn --config "python:config.gunicorn" "snake_eyes.app:create_app()"
    else
        celery worker --beat --app snake_eyes.blueprints.contact.tasks --loglevel info
    fi
fi
