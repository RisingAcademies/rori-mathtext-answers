from mathtext_fastapi.constants import (
    GOOGLE_CLOUD_SQL_HOST,
    GOOGLE_CLOUD_SQL_USER,
    GOOGLE_CLOUD_SQL_PASSWORD,
    GOOGLE_CLOUD_SQL_NAME,
    POSTGRES_DATABASE,
    POSTGRES_USERNAME,
    POSTGRES_PASSWORD,
    POSTGRES_HOST,
    POSTGRES_PORT,
)

import logging

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_TZ = True
DEBUG = True


if POSTGRES_HOST is None and GOOGLE_CLOUD_SQL_HOST is None:
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
