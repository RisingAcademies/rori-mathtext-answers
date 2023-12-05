import django.apps


class DjangoConfig(django.apps.AppConfig):
    name = "mathtext_fastapi.django_logging.django_app"
    verbose_name = "Django logging service for Turn.io message data"
    label = "mathtext_fastapi_api_django_logging"
    default_auto_field = "django.db.models.BigAutoField"