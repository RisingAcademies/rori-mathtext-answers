# Generated by Django 4.2.7 on 2023-12-15 03:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mathtext_fastapi_api_django_logging', '0004_rename_content_activity_properties'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mathanswermessagemetadata',
            name='answer_type',
        ),
    ]