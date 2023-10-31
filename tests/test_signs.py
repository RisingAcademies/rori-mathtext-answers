from fastapi.testclient import TestClient
from tests.simulate_api_call import simulate_api_call
import app

client = TestClient(app.app)


def test_greater_sign_correct_answer():
    response = simulate_api_call(client, ">", ">")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = ">"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_less_or_equal_sign_correct_answer():
    response = simulate_api_call(client, "<=", "<=")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "<="
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_sign_correct_answer_abbreviated():
    response = simulate_api_call(client, "G", ">")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = ">"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_less_or_equal_sign_correct_answer_abbreviated():
    response = simulate_api_call(client, "LTE", "<=")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "<="
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_sign_correct_answer_in_phrase():
    response = simulate_api_call(client, "I think it's >", ">")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = ">"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_against_sign():
    response = simulate_api_call(client, "1/2", ">")
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "1/2"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_decimal_against_sign():
    response = simulate_api_call(client, "1.2", "<")
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "1.2"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_equal_correct_answer():
    response = simulate_api_call(client, "this is =", "=")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "="
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data
