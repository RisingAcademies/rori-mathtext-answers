from mathtext_fastapi.constants import (
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


if POSTGRES_HOST is None:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "db.sqlite3",
        }
    }
    logging.warning("Postgres not configured; using local SQLite db.")
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
