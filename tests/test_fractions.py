from fastapi.testclient import TestClient
from tests.simulate_api_call import simulate_api_call
import app

client = TestClient(app.app)


def test_fraction_correct_answer():
    response = simulate_api_call(client, "3/3", "3/3")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "3/3"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_correct_answer_with_spaces():
    response = simulate_api_call(client, "3 / 3", "3/3")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "3/3"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_correct_answer_in_phrase():
    response = simulate_api_call(client, "that's 3 / 3", "3/3")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "3/3"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_wrong_answer():
    response = simulate_api_call(client, "3/4", "3/3")
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "3/4"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_wrong_answer_in_phrase():
    response = simulate_api_call(client, "it's 3/4", "3/3")
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "3/4"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_against_integer_expected_answer():
    response = simulate_api_call(client, "3/4", "7")
    expected_nlu_response_type = "intent"
    expected_nlu_response_data = "math_answer"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_against_decimal_expected_answer():
    response = simulate_api_call(client, "3/4", "7.0")
    expected_nlu_response_type = "intent"
    expected_nlu_response_data = "math_answer"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_in_phrase_against_integer():
    response = simulate_api_call(client, "that's 3/4", "7")
    expected_nlu_response_type = "intent"
    expected_nlu_response_data = "math_answer"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_in_phrase_against_decimal():
    response = simulate_api_call(client, "I think it's 3/4", "7.0")
    expected_nlu_response_type = "intent"
    expected_nlu_response_data = "math_answer"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_in_phrase_against_word():
    response = simulate_api_call(client, "I think it's 3/4", "Yes")
    expected_nlu_response_type = "intent"
    expected_nlu_response_data = "math_answer"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_in_phrase_against_time():
    response = simulate_api_call(client, "I think it's 11 3/0", "11:30")
    expected_nlu_response_type = "intent"
    expected_nlu_response_data = "math_answer"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data
