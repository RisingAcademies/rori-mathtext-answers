from fastapi.testclient import TestClient
from tests.simulate_api_call import simulate_api_call
import app
from django.test import TestCase
from mathtext_fastapi.django_logging.django_app.models import (
    ActivitySession,
    Message,
    MathAnswerMessageMetadata,
    User,
    UserStatus,
)

client = TestClient(app.app)


def test_activity_session_for_complete_microlesson():
    # Lesson 1: Question 15
    message_context = {
        "author_id": "+1234567",
        "expected_answer": "1",
        "message_body": "1",
        "question_micro_lesson": "G1.N1.1.1.1",
        "question_number": "15",
    }
    response = simulate_api_call(client, message_context)

    # Lesson 1: Question 16
    message_context = {
        "author_id": "+1234567",
        "expected_answer": "1",
        "message_body": "1",
        "question_micro_lesson": "G1.N1.1.1.1",
        "question_number": "16",
    }
    response = simulate_api_call(client, message_context)

    example_user = {"turn_author_id": "+1234567"}

    activity_sessions = ActivitySession.objects.filter(user__properties=example_user)
    assert activity_sessions.count() == 1
    assert activity_sessions[0].status == "CO"


def test_start_new_microlesson_after_completing_previous_microlesson():
    # Lesson 2: Question 1
    message_context = {
        "author_id": "+1234567",
        "expected_answer": "1",
        "message_body": "1",
        "question_micro_lesson": "G2.N1.1.1.1",
        "question_number": "1",
    }
    response = simulate_api_call(client, message_context)

    message_context = {
        "author_id": "+1234567",
        "expected_answer": "1",
        "message_body": "1",
        "question_micro_lesson": "G2.N1.1.1.1",
        "question_number": "2",
    }
    response = simulate_api_call(client, message_context)

    example_user = {"turn_author_id": "+1234567"}
    activity_sessions = ActivitySession.objects.filter(user__properties=example_user)

    assert activity_sessions.count() == 2
    assert activity_sessions[1].status == "IP"
    assert activity_sessions[1].previous_activity_session == activity_sessions[0]


def test_start_new_microlesson_after_interrupting_previous_microlesson():
    # Lesson 3: Question 1
    message_context = {
        "author_id": "+1234567",
        "expected_answer": "1",
        "message_body": "1",
        "question_micro_lesson": "G3.N1.1.1.1",
        "question_number": "1",
    }
    response = simulate_api_call(client, message_context)
    example_user = {"turn_author_id": "+1234567"}
    activity_sessions = ActivitySession.objects.filter(user__properties=example_user)

    assert activity_sessions.count() == 3
    assert activity_sessions[0].status == "CO"
    assert activity_sessions[1].status == "EE"  # Causes an error - IP != EE
    assert activity_sessions[2].status == "IP"
    assert activity_sessions[2].previous_activity_session == activity_sessions[1]


def test_remove_test_generated_records():
    example_user = {"turn_author_id": "+1234567"}

    user_record = User.objects.filter(properties=example_user).first()
    user_status = UserStatus.objects.filter(user=user_record)

    activity_sessions = ActivitySession.objects.filter(user__properties=example_user)

    for session in activity_sessions:
        session.previous_activity_session = None
        session.save()

    activity_session_ids = activity_sessions.values("id")

    messages = Message.objects.filter(activity_session__in=activity_session_ids)
    message_ids = messages.values("id")

    metadata = MathAnswerMessageMetadata.objects.filter(message_id__in=message_ids)

    user_status.delete()
    metadata.delete()
    messages.delete()
    activity_sessions.delete()
    user_record.delete()

    assert True == True
