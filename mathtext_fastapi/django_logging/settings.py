import logging

from mathtext_fastapi.constants import (
    GOOGLE_CLOUD_SQL_HOST,
    GOOGLE_CLOUD_SQL_USER,
    GOOGLE_CLOUD_SQL_PASSWORD,
    GOOGLE_CLOUD_SQL_NAME,
    GOOGLE_CLOUD_SQL_PORT,
    POSTGRES_DATABASE,
    POSTGRES_USERNAME,
    POSTGRES_PASSWORD,
    POSTGRES_HOST,
    POSTGRES_PORT,
)

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_TZ = True
DEBUG = True


if not POSTGRES_HOST and not GOOGLE_CLOUD_SQL_HOST:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "db.sqlite3",
        }
    }
    logging.warning("Postgres not configured; using local SQLite db.")
elif GOOGLE_CLOUD_SQL_HOST:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": GOOGLE_CLOUD_SQL_NAME,
            "USER": GOOGLE_CLOUD_SQL_USER,
            "PASSWORD": GOOGLE_CLOUD_SQL_PASSWORD,
            "HOST": GOOGLE_CLOUD_SQL_HOST,
            "PORT": GOOGLE_CLOUD_SQL_PORT,
        },
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": POSTGRES_DATABASE,
            "USER": POSTGRES_USERNAME,
            "PASSWORD": POSTGRES_PASSWORD,
            "HOST": POSTGRES_HOST,
            "PORT": POSTGRES_PORT,
        },
    }
INSTALLED_APPS = ["mathtext_fastapi.django_logging.django_app.config.DjangoConfig"]
