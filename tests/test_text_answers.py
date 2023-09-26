from fastapi.testclient import TestClient
from tests.simulate_api_call import simulate_api_call
import app

client = TestClient(app.app)


def test_short_true_correct_answer():
    response = simulate_api_call(client, "T", "T")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "T"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_long_true_correct_answer():
    response = simulate_api_call(client, "True", "T")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "T"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_no_false_correct_answer():
    response = simulate_api_call(client, "no", "F")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "F"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_no_correct_answer_in_phrase():
    response = simulate_api_call(client, "That one is false", "F")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "F"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_odd_wrong_answer():
    response = simulate_api_call(client, "odd", "even")
    expected_nlu_response_type = "intent"
    expected_nlu_response_data = "math_answer"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_odd_wrong_answer():
    response = simulate_api_call(client, "odd", "even")
    expected_nlu_response_type = "intent"
    expected_nlu_response_data = "math_answer"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_even_correct_answer_in_phrase():
    response = simulate_api_call(client, "it's even", "even")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "even"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_short_day_of_week_correct_answer():
    response = simulate_api_call(client, "wed", "wednesday")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "wednesday"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_long_day_of_week_correct_answer():
    response = simulate_api_call(client, "Thursday", "thursday")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "thursday"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_short_day_of_week_correct_answer_in_phrase():
    response = simulate_api_call(client, "maybe they'd go on Sat", "saturday")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "saturday"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_short_day_of_week_wrong_answer():
    response = simulate_api_call(client, "mon", "tuesday")
    expected_nlu_response_type = "intent"
    expected_nlu_response_data = "math_answer"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_multiple_choice_correct_answer():
    response = simulate_api_call(client, "a", "A")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "A"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_multiple_choice_wrong_answer():
    response = simulate_api_call(client, "That'd be C", "D")
    expected_nlu_response_type = "intent"
    expected_nlu_response_data = "math_answer"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data
