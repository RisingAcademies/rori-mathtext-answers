from fastapi.testclient import TestClient
from tests.simulate_api_call import simulate_api_call
import app

client = TestClient(app.app)


def test_exponent_correct_answer():
    response = simulate_api_call(client, "1^9", "1^9")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "1^9"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_exponent_wrong_answer():
    response = simulate_api_call(client, "1^5", "1^9")
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "1^5"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_exponent_correct_answer_with_spaces():
    response = simulate_api_call(client, "2 ^ 3", "2^3")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "2^3"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_integer_against_exponent():
    response = simulate_api_call(client, "1159", "11^59")
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "1159"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_decimal_against_exponent():
    response = simulate_api_call(client, "2.3", "2^3")
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "2.3"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_against_exponent():
    response = simulate_api_call(client, "5/4", "5^4")
    expected_nlu_response_type = "intent"
    expected_nlu_response_data = "math_answer"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data
