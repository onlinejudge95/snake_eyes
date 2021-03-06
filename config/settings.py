from datetime import timedelta
from os import environ

from celery.schedules import crontab


LOG_LEVEL = "DEBUG"

SERVER_NAME = environ.get("SERVER_NAME", "localhost:8000")
SECRET_KEY = environ.get("SECRET_KEY")

MAIL_DEFAULT_SENDER = "contact@local.host"
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = environ.get("MAIL_USERNAME")
MAIL_PASSWORD = environ.get("MAIL_PASSWORD")

LANGUAGES = {"en": "English"}
BABEL_DEFAULT_LOCALE = "en"

CELERY_BROKER_URL = environ.get(
    "CELERY_BROKER_URL", "redis://:devpassword@redis:6379/0"
)
CELERY_RESULT_BACKEND = environ.get(
    "CELERY_RESULT_BACKEND", "redis://:devpassword@redis:6379/0"
)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = CELERY_TASK_SERIALIZER
CELERY_REDIS_MAX_CONNECTIONS = 5
CELERY_TASK_LIST = [
    "snake_eyes.blueprints.contact.tasks",
    "snake_eyes.blueprints.user.tasks",
    "snake_eyes.blueprints.billing.tasks",
]
CELERYBEAT_SCHEDULE = {
    "mark-soon-to-expire-credit-cards": {
        "task": "snakeeyes.blueprints.billing.tasks.mark_old_credit_cards",
        "schedule": crontab(hour=0, minute=0),
    },
    "expire-old-coupons": {
        "task": "snakeeyes.blueprints.billing.tasks.expire_old_coupons",
        "schedule": crontab(hour=0, minute=1),
    },
}

SQLALCHEMY_DATABASE_URI = environ.get(
    "SQLALCHEMY_DATABASE_URI",
    "postgresql://snake_eyes:devpassword@postgres:5432/snake_eyes",
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

SEED_ADMIN_EMAIL = environ.get("SEED_ADMIN_EMAIL", "admin@localhost")
SEED_ADMIN_PASSWORD = environ.get("SEED_ADMIN_PASSWORD", "devpassword")
REMEMBER_COOKIE_DURATION = timedelta(days=90)

STRIPE_SECRET_KEY = environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = environ.get("STRIPE_PUBLISHABLE_KEY")
STRIPE_API_VERSION = "2016-03-07"
STRIPE_CURRENCY = "inr"
STRIPE_PLANS = {
    "0": {
        "id": "bronze",
        "name": "Bronze",
        "amount": 100,
        "currency": STRIPE_CURRENCY,
        "interval": "month",
        "interval_count": 1,
        "trial_period_days": 14,
        "statement_descriptor": "SNAKE EYES BRONZE",
        "metadata": {"coins": 110},
    },
    "1": {
        "id": "gold",
        "name": "Gold",
        "amount": 500,
        "currency": STRIPE_CURRENCY,
        "interval": "month",
        "interval_count": 1,
        "trial_period_days": 14,
        "statement_descriptor": "SNAKE EYES GOLD",
        "metadata": {"coins": 600, "recommended": True},
    },
    "2": {
        "id": "platinum",
        "name": "Platinum",
        "amount": 1000,
        "currency": STRIPE_CURRENCY,
        "interval": "month",
        "interval_count": 1,
        "trial_period_days": 14,
        "statement_descriptor": "SNAKE EYES PLATINUM",
        "metadata": {"coins": 1500},
    },
}

COIN_BUNDLES = [
    {"coins": 100, "price_in_cents": 100, "label": "100 for ???75"},
    {"coins": 1000, "price_in_cents": 900, "label": "1,000 for ???670"},
    {"coins": 5000, "price_in_cents": 4000, "label": "5,000 for ???2980"},
    {"coins": 10000, "price_in_cents": 7000, "label": "10,000 for ???5220"},
]

DICE_ROLL_PAYOUT = {
    "2": 36.0,
    "3": 18.0,
    "4": 12.0,
    "5": 9.0,
    "6": 7.2,
    "7": 6.0,
    "8": 7.2,
    "9": 9.0,
    "10": 12.0,
    "11": 18.0,
    "12": 36.0,
}

RATELIMIT_STORAGE_URL = CELERY_BROKER_URL
RATELIMIT_STRATEGY = "fixed-window-elastic-expiry"
RATELIMIT_HEADERS_ENABLED = True

ANALYTICS_GOOGLE_UA = environ.get("ANALYTICS_GOOGLE_UA")
EMAIL_SERVICE_HOST = environ.get("EMAIL_SERVICE_HOST")
