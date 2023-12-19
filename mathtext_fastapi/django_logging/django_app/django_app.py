import django
import django.apps


class DjangoConfig(django.apps.AppConfig):
    name = "mathtext_fastapi.django_logging"
    verbose_name = "Django logging service for Turn.io message data"
    label = "mathtext_fastapi_api_django_logging"