"""
Some logging functions on this file use transaction.atomic.
- https://docs.djangoproject.com/en/4.2/topics/db/transactions/

DBError-related exceptions will cause all DB transactions nested inside transactions.atomic to be rolled back.  Need to be careful with Exception handling logic.
- https://stackoverflow.com/questions/42586841/is-it-ok-to-catch-and-reraise-an-exception-inside-django-transaction-atomic
"""
import asyncio
import logging

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

log = logging.getLogger(__name__)


def retrieve_user_status(is_new_user, user):
    """Retrieves the UserStatus instance for a given User or creates it if the user is new"""
    user_status = None
    if is_new_user:
        user_status_context = {"user": user, "current_activity_session": None}
        user_status = UserStatus.objects.create(**user_status_context)

    if not user_status:
        user_status = UserStatus.objects.filter(user=user).first()
    return user_status


def update_activity_session(user_status, question_number):
    """Update an ActivitySession that has concluded

    Possible conclusions are CO (complete) or EE (early exit)
    """
    if question_number == "16":
        user_status.current_activity_session.status = (
            ActivitySession.ActivitySessionStatus.COMPLETE
        )
    elif user_status.previous_activity_session.status == "CO":
        # ActivitySession not updated when student finished it
        pass
    else:
        user_status.current_activity_session.status = (
            ActivitySession.ActivitySessionStatus.EARLY_EXIT
        )
    user_status.current_activity_session.save()
    return user_status.current_activity_session


def update_user_status(user_status, activity_session):
    """Updates the current and past activity_sessions through the UserStatus model"""
    try:
        old_session = user_status.current_activity_session
    except:
        # Handles first time user
        old_session = None
    user_status.current_activity_session = activity_session
    user_status.current_activity_session.previous_activity_session = old_session
    user_status.save()

    return user_status


def create_new_activity_session(user, activity, line_number):
    status = ActivitySession.ActivitySessionStatus.IN_PROGRESS

    properties = {}

    if ("bkt_params" in activity.properties) and (
        line_number in activity.properties["bkt_params"]
    ):
        properties["bkt_params"] = {}
        properties["bkt_params"]["p_learn"] = activity.properties["bkt_params"][
            line_number
        ]["l0"]
        properties["bkt_params"]["p_guess"] = activity.properties["bkt_params"][
            line_number
        ]["p_guess"]
        properties["bkt_params"]["p_slip"] = activity.properties["bkt_params"][
            line_number
        ]["p_slip"]
        properties["bkt_params"]["p_transit"] = activity.properties["bkt_params"][
            line_number
        ]["p_transit"]

    current_activity_session_context = {
        "activity": activity,
        "user": user,
        "status": status,
        "properties": properties,
    }
    activity_session = ActivitySession.objects.create(
        **current_activity_session_context
    )
    return activity_session


def update_user_and_activity_context(
    user, user_status, activity, line_number, question_number
):
    """Update activity session through UserStatus and creates new activity session when necessary

    A new ActivitySession should not be created on the last question of a microlesson (Q#16)
    """
    update_activity_session(user_status, question_number)
    if question_number != "16":
        activity_session = create_new_activity_session(user, activity, line_number)
    else:
        activity_session = user_status.current_activity_session
    return activity_session


def retrieve_activity_session(
    user, user_status, activity, line_number, question_number
):
    """Returns the most current ActivitySession for a user"""
    activity_session = None
    try:
        if (
            user_status.current_activity_session.activity.id != activity.id
            or question_number == "16"
        ):
            activity_session = update_user_and_activity_context(
                user, user_status, activity, line_number, question_number
            )
            update_user_status(user_status, activity_session)
    except AttributeError as e:
        activity_session = create_new_activity_session(user, activity, line_number)
        update_user_status(user_status, activity_session)
    if not activity_session:
        activity_session = user_status.current_activity_session
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
        "user_attempts": message_data["user_attempts"],
    }
    message_metadata = MathAnswerMessageMetadata.objects.create(
        **message_metadata_context
    )
    return message_metadata


@database_sync_to_async
def get_user_model(message_data):
    with transaction.atomic():
        user, created = User.objects.get_or_create(
            properties={
                "turn_author_id": message_data["author_id"]
            }  # TODO: Revise later to use contact_uuid
        )

        user_status = retrieve_user_status(created, user)

        content_unit_name = message_data.get("question_micro_lesson", "")
        activity = Activity.objects.get(name=content_unit_name)

        line_number = message_data.get("line_number", "")
        question_number = message_data.get("question_number", "0")
        activity_session = retrieve_activity_session(
            user, user_status, activity, line_number, question_number
        )
        return user, user_status, activity, activity_session


@database_sync_to_async
def update_p_learn(activity_session, new_p_learn):
    try:
        activity_session.properties["bkt_params"]["p_learn"] = new_p_learn
        activity_session.save()
    except Exception as e:
        log.warning(f"Unable to save new_p_learn to ActivitySession.properties")
        log.warning(str(e))
        raise


# TODO: need to add validation for each instance
@database_sync_to_async
def log_user_and_message_context(message_data, nlu_response, activity_session):
    """Uses Turn.io context data to create log records of
    User, UserStatus, UserProperties,
    Activity, ActivitySession
    Message, MathAnswerMessageMetadata

    All DB queries must succeed or changes are rolled back
    """
    with transaction.atomic():
        log_bot_message(activity_session, message_data)

        student_message = log_student_message(activity_session, message_data)

        log_message_metadata(student_message, message_data, nlu_response)


# async def main():
#     message_data = {
#         "author_id": "57787919091",
#         "author_type": "OWNER",
#         "contact_uuid": "df78gsdf78df",
#         "message_direction": "inbound",
#         "message_id": "ABGGIyd4CZSfAhANH3bakk0ByOtSYj8I7Dxz",
#         "line_number": "+12062587201",
#         "message_inserted_at": "2023-05-31T13:20:25.779686Z",
#         "message_updated_at": "2023-05-31T13:57:40.650739Z",
#         "question_micro_lesson": "G1.N1.3.1.1",
#         "question": "___, 27, 28, 29, 30",
#         "question_level": "1",
#         "question_skill": "Fractions",
#         "question_topic": "Fractions",
#         "question_number": "1",
#         "expected_answer": "2,253",
#         "message_body": "maybe 26.5",
#     }
#     user, user_status, activity, activity_session = await get_user_model(message_data)
#     print(user)
#     print(user_status)
#
# if __name__ == "__main__":
#     asyncio.run(main())
