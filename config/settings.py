from datetime import timedelta

from celery.schedules import crontab


DEBUG = True
LOG_LEVEL = "DEBUG"

SERVER_NAME = "localhost:8000"
SECRET_KEY = "secret_key"

MAIL_DEFAULT_SENDER = "contact@local.host"
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = "user@gmail.com"
MAIL_PASSWORD = "password"

CELERY_BROKER_URL = "redis://:devpassword@redis:6379/0"
CELERY_RESULT_BACKEND = "redis://:devpassword@redis:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_REDIS_MAX_CONNECTIONS = 5
CELERY_TASK_LIST = [
    "snake_eyes.blueprints.contact.tasks",
    "snake_eyes.blueprints.user.tasks",
    "snake_eyes.blueprints.billing.tasks",
]
CELERYBEAT_SCHEDULE = {
    "mark-soon-to-expire-credit-cards": {
        "task": "snakeeyes.blueprints.billing.tasks.mark_old_credit_cards",
        "schedule": crontab(hour=0, minute=0)
    },
    "expire-old-coupons": {
        "task": "snakeeyes.blueprints.billing.tasks.expire_old_coupons",
        "schedule": crontab(hour=0, minute=1)
    },
}

SQLALCHEMY_DATABASE_URI = "postgresql://snake_eyes:devpassword@postgres:5432/snake_eyes"  # noqa: E501
SQLALCHEMY_TRACK_MODIFICATIONS = False

SEED_ADMIN_EMAIL = "dev@localhost"
SEED_ADMIN_PASSWORD = "devpassword"
REMEMBER_COOKIE_DURATION = timedelta(days=90)

STRIPE_SECRET_KEY = None
STRIPE_PUBLISHABLE_KEY = None
STRIPE_API_VERSION = "2016-03-07"
STRIPE_PLANS = {
    "0": {
        "id": "bronze",
        "name": "Bronze",
        "amount": 100,
        "currency": "usd",
        "interval": "month",
        "interval_count": 1,
        "trial_period_days": 14,
        "statement_descriptor": "SNAKE EYES BRONZE",
        "metadata": {}
    },
    "1": {
        "id": "gold",
        "name": "Gold",
        "amount": 500,
        "currency": "usd",
        "interval": "month",
        "interval_count": 1,
        "trial_period_days": 14,
        "statement_descriptor": "SNAKE EYES GOLD",
        "metadata": {
            "recommended": True
        }
    },
    "2": {
        "id": "platinum",
        "name": "Platinum",
        "amount": 1000,
        "currency": "usd",
        "interval": "month",
        "interval_count": 1,
        "trial_period_days": 14,
        "statement_descriptor": "SNAKE EYES PLATINUM",
        "metadata": {}
    },
}
