from fastapi.testclient import TestClient
from tests.simulate_api_call import simulate_api_call
import app

client = TestClient(app.app)


def test_designate_out_of_scope_to_nonsense_utterance():
    message_context = {
        "expected_answer": "4,000",
        "message_body": "maybe 2djkajdajk",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "out_of_scope"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type


def test_designate_out_of_scope_to_irrelevant_utterance():
    message_context = {
        "expected_answer": "4,000",
        "message_body": "Please send me data",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "out_of_scope"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type


def test_designate_request_for_menu_as_intent():
    message_context = {
        "expected_answer": "374",
        "message_body": "let me choose something else",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "intent"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type


def test_designate_request_for_hint_as_intent():
    message_context = {
        "expected_answer": "374",
        "message_body": "I need an explanation",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "intent"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type


def test_return_student_message_for_out_of_scope_data():
    message_context = {
        "expected_answer": "22",
        "message_body": "dakjagjlkajlag",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_data = "dakjagjlkajlag"
    assert response.status_code == 200
    assert response.json()["data"] == expected_nlu_response_data


def test_yes_answer_intent():
    message_context = {
        "expected_answer": "yes",
        "message_body": "sure",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "yes"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data
