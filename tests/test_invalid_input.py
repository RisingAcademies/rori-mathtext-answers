from fastapi.testclient import TestClient
from tests.simulate_api_call import simulate_api_call
import app

client = TestClient(app.app)


def test_detect_profanity_word():
    message_context = {
        "expected_answer": "374",
        "message_body": "fuck",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "intent"
    expected_nlu_response_data = "profanity"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_detect_profanity_with_spaces():
    message_context = {
        "expected_answer": "374",
        "message_body": "f u c k this math it's 100",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "intent"
    expected_nlu_response_data = "profanity"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_detect_old_button_message_with_emoji():
    message_context = {
        "expected_answer": "374",
        "message_body": "No 😕",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "intent"
    expected_nlu_response_data = "old_button"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_detect_old_button_message_():
    message_context = {
        "expected_answer": "374",
        "message_body": "Continue",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "intent"
    expected_nlu_response_data = "old_button"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data
