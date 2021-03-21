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

broker_url = "redis://:password@redis:6379/0"
result_backend = "redis://:password@redis:6379/0"
accept_content = ["json"]
task_serializer = "json"
result_serializer = "json"
redis_max_connections = 5
CELERY_TASK_LIST = ["snake_eyes.blueprints.contact.tasks"]
