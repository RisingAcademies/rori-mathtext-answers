from datetime import datetime, timezone

from django.db import models
from django.utils.translation import gettext_lazy

from mathtext_fastapi.django_logging import utils

utils.ensure_django()


def get_current_datetime():
    return datetime.now(timezone.utc)


class User(models.Model):
    created_at = models.DateTimeField(default=get_current_datetime)
    updated_at = models.DateTimeField(auto_now=True)
    properties = models.JSONField()

    class Meta:
        db_table = "user"


class Activity(models.Model):
    name = models.TextField(unique=True)
    type = models.TextField()
    properties = models.JSONField()
    created_at = models.DateTimeField(default=get_current_datetime)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "activity"


class ActivitySession(models.Model):
    class ActivitySessionStatus(models.TextChoices):
        IN_PROGRESS = "IP", gettext_lazy("In-progress")
        EARLY_EXIT = "EE", gettext_lazy("Early exit")
        COMPLETE = "CO", gettext_lazy("Completed")

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    activity = models.ForeignKey(Activity, on_delete=models.PROTECT)
    previous_activity_session = models.ForeignKey(
        "self", on_delete=models.PROTECT, null=True
    )

    status = models.CharField(
        max_length=2,
        choices=ActivitySessionStatus.choices,
        default=ActivitySessionStatus.IN_PROGRESS,
    )
    created_at = models.DateTimeField(default=get_current_datetime)
    updated_at = models.DateTimeField(auto_now=True)

    properties = models.JSONField(default=dict)

    class Meta:
        db_table = "activity_session"


class Message(models.Model):
    class MessageDirection(models.TextChoices):
        INBOUND = "I", gettext_lazy("Inbound")
        OUTBOUND = "O", gettext_lazy("Outbound")

    activity_session = models.ForeignKey(ActivitySession, on_delete=models.PROTECT)
    bq_message_id = models.TextField(null=True)
    previous_message = models.ForeignKey("self", on_delete=models.PROTECT, null=True)

    text = models.TextField()
    direction = models.CharField(
        max_length=1,
        choices=MessageDirection.choices,
        default=MessageDirection.OUTBOUND,
    )
    created_at = models.DateTimeField(default=get_current_datetime)

    class Meta:
        db_table = (
            "rori_message"  # TODO: Change this to 'message' after adjusting tests
        )


class MathAnswerMessageMetadata(models.Model):
    message = models.ForeignKey(Message, on_delete=models.PROTECT)
    question_level = models.IntegerField()
    question_skill = models.TextField()
    question_topic = models.TextField()
    question_number = models.TextField()
    expected_answer = models.TextField()
    question_micro_lesson = models.TextField()
    nlu_response_data = models.TextField()
    nlu_response_type = models.TextField()
    nlu_response_confidence = models.TextField()
    hint_shown = models.TextField(null=True)
    user_attempts = models.IntegerField(default=0)

    class Meta:
        db_table = "math_answer_message_metadata"


class UserStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    current_activity_session = models.ForeignKey(
        ActivitySession, on_delete=models.PROTECT, null=True
    )
    created_at = models.DateTimeField(default=get_current_datetime)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_status"


class UserProperties(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    name = models.TextField()
    value = models.TextField()

    class Meta:
        db_table = "user_properties"
