from fastapi.testclient import TestClient
from tests.simulate_api_call import simulate_api_call
import app

client = TestClient(app.app)


def test_time_correct_answer():
    message_context = {
        "expected_answer": "11:30",
        "message_body": "11:30",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "11:30"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_time_wrong_answer():
    message_context = {
        "expected_answer": "11:30",
        "message_body": "12:30",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "12:30"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_time_wrong_answer_missing_colon():
    message_context = {
        "expected_answer": "11:30",
        "message_body": "1130",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "1130"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_time_correct_answer_with_spaces():
    message_context = {
        "expected_answer": "17:03",
        "message_body": "17 : 03",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "17:03"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_time_correct_answer_leading_zero():
    message_context = {
        "expected_answer": "1:15",
        "message_body": "01:15",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "1:15"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_time_correct_answer_in_phrase():
    message_context = {
        "expected_answer": "2:42",
        "message_body": "that is 2:42",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "2:42"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_time_correct_answer_with_am():
    message_context = {
        "expected_answer": "14:40",
        "message_body": "14:40 AM",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "14:40"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_decimal_against_time_answer():
    message_context = {
        "expected_answer": "1:30",
        "message_body": "1.3",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "1.3"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_integer_against_time_answer():
    message_context = {
        "expected_answer": "5:00",
        "message_body": "5",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "5"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_against_time_answer():
    message_context = {
        "expected_answer": "1:30",
        "message_body": "1/30",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "1/30"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data
