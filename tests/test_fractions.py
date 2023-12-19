from fastapi.testclient import TestClient
from tests.simulate_api_call import simulate_api_call
import app

client = TestClient(app.app)


def test_fraction_correct_answer():
    message_context = {
        "expected_answer": "3/3",
        "message_body": "3/3",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "3/3"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_correct_answer_with_spaces():
    message_context = {
        "expected_answer": "3/3",
        "message_body": "3 / 3",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "3/3"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_correct_answer_in_phrase():
    message_context = {
        "expected_answer": "3/3",
        "message_body": "that's 3 / 3",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "3/3"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_wrong_answer():
    message_context = {
        "expected_answer": "3/3",
        "message_body": "3/4",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "3/4"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_wrong_answer_in_phrase():
    message_context = {
        "expected_answer": "3/3",
        "message_body": "it's 3/4",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "3/4"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_against_integer_expected_answer():
    message_context = {
        "expected_answer": "7",
        "message_body": "3/4",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "3/4"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_against_decimal_expected_answer():
    message_context = {
        "expected_answer": "7.0",
        "message_body": "3/4",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "3/4"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_in_phrase_against_integer():
    message_context = {
        "expected_answer": "7",
        "message_body": "that's 3/4",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "3/4"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_in_phrase_against_decimal():
    message_context = {
        "expected_answer": "7.0",
        "message_body": "I think it's 3/4",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "3/4"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_in_phrase_against_word():
    message_context = {
        "expected_answer": "Yes",
        "message_body": "I think it's 3/4",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "3/4"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_in_phrase_against_time():
    message_context = {
        "expected_answer": "11:30",
        "message_body": "I think it's 11 3/0",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "11 3/0"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data
