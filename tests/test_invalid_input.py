from fastapi.testclient import TestClient
from tests.simulate_api_call import simulate_api_call
import app

client = TestClient(app.app)


def test_detect_profanity_word():
    response = simulate_api_call(client, "fuck", "374")
    expected_nlu_response_type = "intent"
    expected_nlu_response_data = "profanity"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_detect_profanity_with_spaces():
    response = simulate_api_call(client, "f u c k this math it's 100", "374")
    expected_nlu_response_type = "intent"
    expected_nlu_response_data = "profanity"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_detect_old_button_message_with_emoji():
    response = simulate_api_call(client, "No 😕", "374")
    expected_nlu_response_type = "intent"
    expected_nlu_response_data = "old_button"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_detect_old_button_message_():
    response = simulate_api_call(client, "Continue", "374")
    expected_nlu_response_type = "intent"
    expected_nlu_response_data = "old_button"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data
