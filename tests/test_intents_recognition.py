from fastapi.testclient import TestClient
from tests.simulate_api_call import simulate_api_call
import app

client = TestClient(app.app)


def test_designate_out_of_scope_to_nonsense_utterance():
    response = simulate_api_call(client, "maybe 2djkajdajk", "4,000")
    expected_nlu_response_type = "out_of_scope"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type


def test_designate_out_of_scope_to_irrelevant_utterance():
    response = simulate_api_call(client, "Please send me data", "4,000")
    expected_nlu_response_type = "out_of_scope"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type


def test_designate_request_for_menu_as_intent():
    response = simulate_api_call(client, "let me choose something else", "374")
    expected_nlu_response_type = "intent"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type


def test_designate_request_for_hint_as_intent():
    response = simulate_api_call(client, "I need an explanation", "374")
    expected_nlu_response_type = "intent"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type


def test_return_student_message_for_out_of_scope_data():
    response = simulate_api_call(client, "dakjagjlkajlag", "22")
    expected_nlu_response_data = "dakjagjlkajlag"
    assert response.status_code == 200
    assert response.json()["data"] == expected_nlu_response_data


def test_yes_answer_intent():
    response = simulate_api_call(client, "sure", "yes")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "yes"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data
