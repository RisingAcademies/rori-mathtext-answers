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


def retrieve_user_status(is_new_user, user, activity):
    """Retrieves the UserStatus instance for a given User or creates it if the user is new"""
    user_status = None
    if is_new_user:
        user_status_context = {"user": user, "current_activity": activity}
        user_status = UserStatus.objects.create(**user_status_context)

    if not user_status:
        user_status = UserStatus.objects.filter(user=user).first()
    return user_status


def update_activity_session(user, user_status, activity):
    """Update the old ActivitySession and create a new ActivitySession"""
    # Find/Update the last activity session of a student
    previous_activity_session = (
        ActivitySession.objects.filter(user=user).order_by("-id").first()
    )
    previous_activity_session.status = ActivitySession.ActivitySessionStatus.EARLY_EXIT
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
    return activity_session


def retrieve_activity_session(user, user_status, activity):
    """Returns the most current ActivitySession for a user"""
    activity_session = None
    if user_status.current_activity.id != activity.id:
        activity_session = update_activity_session(user, user_status, activity)
    if not activity_session:
        activity_session = (
            ActivitySession.objects.filter(user_id=user).order_by("-id").first()
        )
    return activity_session


def log_bot_message(activity_session, message_data):
    """Logs the chatbot's message that the user responded to"""
    bot_message_context = {
        "activity_session": activity_session,
        "text": message_data["question"],
        "direction": Message.MessageDirection.OUTBOUND,
    }
    bot_message = Message.objects.create(**bot_message_context)
    return bot_message


def log_student_message(activity_session, message_data):
    """Logs a student's response to a chatbot message"""
    student_message_context = {
        "activity_session": activity_session,
        "bq_message_id": message_data["message_id"],
        "text": message_data["message_body"],
        "direction": Message.MessageDirection.INBOUND,
    }
    student_message = Message.objects.create(**student_message_context)
    return student_message


def log_message_metadata(student_message, message_data, nlu_response):
    """Logs additional context of the student message"""
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
    return message_metadata


# TODO: need to add validation for each instance
@database_sync_to_async
def log_user_and_message_context(message_data, nlu_response):
    """Uses Turn.io context data to create log records of
    User, UserStatus, UserProperties,
    Activity, ActivitySession
    Message, MathAnswerMessageMetadata

    All DB queries must succeed or changes are rolled back
    """
    with transaction.atomic():
        # if True:
        content_unit_name = message_data.get("question_micro_lesson", "")
        activity = Activity.objects.get(name=content_unit_name)

        user, created = User.objects.get_or_create(
            properties={"turn_author_id": message_data["author_id"]}  # Revise later
        )

        user_status = retrieve_user_status(created, user, activity)

        activity_session = retrieve_activity_session(user, user_status, activity)

        bot_message = log_bot_message(activity_session, message_data)

        student_message = log_student_message(activity_session, message_data)

        message_metadata = log_message_metadata(
            student_message, message_data, nlu_response
        )
