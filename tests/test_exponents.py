from fastapi.testclient import TestClient
from tests.simulate_api_call import simulate_api_call
import app

client = TestClient(app.app)


def test_exponent_correct_answer():
    message_context = {
        "expected_answer": "1^9",
        "message_body": "1^9",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "1^9"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_exponent_wrong_answer():
    message_context = {
        "expected_answer": "1^9",
        "message_body": "1^5",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "1^5"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_exponent_correct_answer_with_spaces():
    message_context = {
        "expected_answer": "2^3",
        "message_body": "2 ^ 3",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "2^3"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_integer_against_exponent():
    message_context = {
        "expected_answer": "11^59",
        "message_body": "1159",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "1159"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_decimal_against_exponent():
    message_context = {
        "expected_answer": "2^3",
        "message_body": "2.3",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "2.3"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_against_exponent():
    message_context = {
        "expected_answer": "5^4",
        "message_body": "5/4",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "5/4"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data
