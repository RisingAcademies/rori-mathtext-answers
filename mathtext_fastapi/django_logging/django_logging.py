# from asgiref.sync import sync_to_async

from channels.db import database_sync_to_async
from django.db import transaction

from mathtext_fastapi.django_logging.django_app.models import (
    Activity,
    ActivitySession,
    MathAnswerMessageMetadata,
    Message,
    User,
    UserProperties,
    UserStatus,
)


# TODO: need to add validation for each instance
@database_sync_to_async
def log_message_context(message_data, nlu_response):
    content_unit_name = message_data.get("question_micro_lesson", "")
    activity = Activity.objects.get(name=content_unit_name)
    user_status = None
    activity_session = None
    user, created = User.objects.get_or_create(
        properties={"turn_author_id": message_data["author_id"]}  # Revise later
    )

    if created:
        user_status_context = {"user": user, "current_activity": activity}
        user_status = UserStatus.objects.create(**user_status_context)
        user_properties_context = {"user": user, "name": "test", "value": "test"}
        user_properties = UserProperties.objects.create(**user_properties_context)

    if not user_status:
        user_status = UserStatus.objects.filter(user=user).first()

    with transaction.atomic():
        if user_status.current_activity.id != activity.id:
            # Update old ActivitySession
            previous_activity_session = ActivitySession.objects.filter(id=activity.id)
            previous_activity_session.status = (
                ActivitySession.ActivitySessionStatus.EARLY_EXIT
            )
            previous_activity_session.save()

            # Update User Status with new Activity
            user_status.current_activity = activity
            user_status.save()

            # Create new ActivitySession
            status = ActivitySession.ActivitySessionStatus.IN_PROGRESS
            current_activity_session_context = {
                "activity": activity,
                "user": user,
                "status": status,
            }
            activity_session = ActivitySession.objects.create(
                **current_activity_session_context
            )

        if not activity_session:
            activity_session = (
                ActivitySession.objects.filter(user_id=user).order_by("-id").first()
            )

        # 6. Build and save Bot Message
        bot_message_context = {
            "activity_session": activity_session,
            "text": message_data["question"],
            "direction": Message.MessageDirection.OUTBOUND,
        }
        bot_message = Message.objects.create(**bot_message_context)

        # 7. Build and save Student Message
        student_message_context = {
            "activity_session": activity_session,
            "bq_message_id": message_data["message_id"],
            "text": message_data["message_body"],
            "direction": Message.MessageDirection.INBOUND,
        }
        student_message = Message.objects.create(**student_message_context)

        # 8. Build and create MessageMetadata
        message_metadata_context = {
            "message_id": student_message.id,  # Student Message
            "question_level": message_data["question_level"],
            "question_skill": message_data["question_skill"],
            "question_topic": message_data["question_topic"],
            "question_number": message_data["question_number"],
            "expected_answer": message_data["expected_answer"],
            "question_micro_lesson": message_data["question_micro_lesson"],
            "nlu_response_type": nlu_response["type"],
            "nlu_response_data": nlu_response["data"],
            "nlu_response_confidence": nlu_response["confidence"],
        }
        message_metadata = MathAnswerMessageMetadata.objects.create(
            **message_metadata_context
        )
