from fastapi.testclient import TestClient
from tests.simulate_api_call import simulate_api_call
import app

client = TestClient(app.app)


def test_lesson_mastery_for_correct_answer():
    message_context = {
        "expected_answer": "1",
        "message_body": "1",
        "question_micro_lesson": "G1.N1.1.1.1",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["mastery"] > 0.99
    assert response.json()["mastery"] < 1.0


def test_lesson_mastery_for_wrong_answer():
    message_context = {
        "expected_answer": "1",
        "message_body": "0",
        "question_micro_lesson": "G1.N1.1.1.1",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["mastery"] > 0.67
    assert response.json()["mastery"] < 0.7


def test_lesson_mastery_for_intent_response():
    message_context = {
        "expected_answer": "1",
        "message_body": "I dont know",
        "question_micro_lesson": "G1.N1.1.1.1",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "intent"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["mastery"] == 0.893


def test_lesson_mastery_when_no_bkt_parameters():
    message_context = {
        "expected_answer": "1",
        "message_body": "0",
        "question_micro_lesson": "G1.N1.3.1.2",
    }
    response = simulate_api_call(client, message_context)
    assert response.status_code == 200
    assert response.json()["mastery"] is -1


def test_lesson_mastery_with_updated_user_attempt():
    message_context = {
        "expected_answer": "1",
        "message_body": "0",
        "question_micro_lesson": "G1.N1.3.1.2",
        "user_attempts": "5",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["mastery"] is -1
