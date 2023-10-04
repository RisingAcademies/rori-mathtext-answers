from fastapi.testclient import TestClient
from tests.simulate_api_call import simulate_api_call
import app

client = TestClient(app.app)


def test_time_correct_answer():
    response = simulate_api_call(client, "11:30", "11:30")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "11:30"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_time_wrong_answer():
    response = simulate_api_call(client, "12:30", "11:30")
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "12:30"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_time_wrong_answer_missing_colon():
    response = simulate_api_call(client, "1130", "11:30")
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "1130"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_time_correct_answer_with_spaces():
    response = simulate_api_call(client, "17 : 03", "17:03")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "17:03"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_time_correct_answer_leading_zero():
    response = simulate_api_call(client, "01:15", "1:15")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "1:15"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_time_correct_answer_in_phrase():
    response = simulate_api_call(client, "that is 2:42", "2:42")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "2:42"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_time_correct_answer_with_am():
    response = simulate_api_call(client, "14:40 AM", "14:40")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "14:40"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_decimal_against_time_answer():
    response = simulate_api_call(client, "1.30", "1:30")
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "1.3"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_integer_against_time_answer():
    response = simulate_api_call(client, "5", "5:00")
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "5"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_fraction_against_time_answer():
    response = simulate_api_call(client, "1/30", "1:30")
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "1/30"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data
