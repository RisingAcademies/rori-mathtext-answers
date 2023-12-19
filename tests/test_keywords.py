from fastapi.testclient import TestClient
from tests.simulate_api_call import simulate_api_call
import app

client = TestClient(app.app)


def test_designate_menu_as_keyword():
    message_context = {
        "expected_answer": "374",
        "message_body": "menu",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "keyword"
    expected_nlu_response_data = "menu"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_designate_menu_misspelling_as_keyword():
    message_context = {
        "expected_answer": "374",
        "message_body": "manu",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "keyword"
    expected_nlu_response_data = "menu"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_designate_help_as_keyword():
    message_context = {
        "expected_answer": "374",
        "message_body": "help",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "keyword"
    expected_nlu_response_data = "help"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_designate_stop_as_keyword():
    message_context = {
        "expected_answer": "374",
        "message_body": "stop",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "keyword"
    expected_nlu_response_data = "stop"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_designate_support_as_keyword():
    message_context = {
        "expected_answer": "374",
        "message_body": "support",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "keyword"
    expected_nlu_response_data = "support"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data
