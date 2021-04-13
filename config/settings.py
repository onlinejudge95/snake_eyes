DEBUG = True

SERVER_NAME = "localhost:8000"
SECRET_KEY = "secret_key"

MAIL_DEFAULT_SENDER = "user@host"
MAIL_SERVER = "localhost"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = "user@email.com"
MAIL_PASSWORD = "password"

CELERY_BROKER_URL = "redis://:devpassword@redis:6379/0"
CELERY_RESULT_BACKEND = "redis://:devpassword@redis:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_REDIS_MAX_CONNECTIONS = 5
CELERY_TASK_LIST = [
    "snake_eyes.blueprints.contact.tasks",
    "snake_eyes.blueprints.user.tasks"
]

db_string = "postgresql://snake_eyes:devpassword@postgres:5432/snake_eyes"
SQLALCHEMY_DATABASE_URI = db_string
SQLALCHEMY_TRACK_MODIFICATIONS = False
