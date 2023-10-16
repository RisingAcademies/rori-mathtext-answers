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
    response = simulate_api_call(client, "odd", "Even")
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "Odd"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_even_correct_answer_in_phrase():
    response = simulate_api_call(client, "it's even", "Even")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "Even"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_short_day_of_week_correct_answer():
    response = simulate_api_call(client, "wed", "Wednesday")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "Wednesday"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_long_day_of_week_correct_answer():
    response = simulate_api_call(client, "Thursday", "Thursday")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "Thursday"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_short_day_of_week_correct_answer_in_phrase():
    response = simulate_api_call(client, "maybe they'd go on Sat", "Saturday")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "Saturday"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_short_day_of_week_wrong_answer():
    response = simulate_api_call(client, "mon", "Tuesday")
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "Monday"
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
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "C"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_multiple_choice_wrong_answer():
    response = simulate_api_call(client, "yep", "10")
    expected_nlu_response_type = "out_of_scope"
    expected_nlu_response_data = "yep"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_multiple_choice_wrong_answer():
    response = simulate_api_call(client, "sure", "yes")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "yes"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_multiple_choice_wrong_answer():
    response = simulate_api_call(client, "I want a hint", "B")
    expected_nlu_response_type = "intent"
    expected_nlu_response_data = "math_question"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_yes_no_wrong_answer():
    response = simulate_api_call(client, "Yes", "No")
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "yes"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data
