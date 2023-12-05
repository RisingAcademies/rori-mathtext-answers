from mathtext_fastapi.constants import POSTGRES_URL

import logging

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_TZ = True


if POSTGRES_URL is None:
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
            "NAME": POSTGRES_URL.get("database", ""),
            "USER": POSTGRES_URL.get("username", ""),
            "PASSWORD": POSTGRES_URL.get("password", ""),
            "HOST": POSTGRES_URL.get("host", ""),
            "PORT": POSTGRES_URL.get("port", ""),
        },
    }
    logging.info(f"Using Postgres {POSTGRES_URL.get('host','')}")
INSTALLED_APPS = ["mathtext_fastapi.django_logging.django_app.config.DjangoConfig"]
