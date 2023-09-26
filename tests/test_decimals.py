from fastapi.testclient import TestClient
from tests.simulate_api_call import simulate_api_call
import app

client = TestClient(app.app)


def test_decimal_correct_answer():
    response = simulate_api_call(client, "14.5", "14.5")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "14.5"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_decimal_wrong_answer():
    response = simulate_api_call(client, "2.5", "1.5")
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "2.5"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_decimal_with_double_decimal_points():
    response = simulate_api_call(client, "2..5", "2.5")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "2.5"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_decimal_with_double_extra_spacing():
    response = simulate_api_call(client, "4 . 4", "4.4")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "4.4"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_decimal_against_integer():
    response = simulate_api_call(client, "4 . 4", "44")
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "4.4"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_decimal_right_answer_in_phrase():
    response = simulate_api_call(client, "that one is 78.2", "78.2")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "78.2"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_decimal_wrong_answer_in_phrase():
    response = simulate_api_call(client, "The answer is 54.4", "54.0")
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "54.4"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_again_decimal():
    response = simulate_api_call(client, "3/0", "3.0")
    expected_nlu_response_type = "intent"
    expected_nlu_response_data = "math_answer"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data
