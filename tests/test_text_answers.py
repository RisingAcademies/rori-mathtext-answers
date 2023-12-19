from fastapi.testclient import TestClient
from tests.simulate_api_call import simulate_api_call
import app

client = TestClient(app.app)


def test_short_true_correct_answer():
    message_context = {
        "expected_answer": "T",
        "message_body": "T",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "T"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_long_true_correct_answer():
    message_context = {
        "expected_answer": "T",
        "message_body": "True",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "T"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_no_false_correct_answer():
    message_context = {
        "expected_answer": "F",
        "message_body": "no",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "F"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_no_correct_answer_in_phrase():
    message_context = {
        "expected_answer": "F",
        "message_body": "That one is false",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "F"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_odd_wrong_answer():
    message_context = {
        "expected_answer": "Even",
        "message_body": "odd",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "Odd"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_even_correct_answer_in_phrase():
    message_context = {
        "expected_answer": "Even",
        "message_body": "it's even",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "Even"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_short_day_of_week_correct_answer():
    message_context = {
        "expected_answer": "Wednesday",
        "message_body": "wed",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "Wednesday"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_long_day_of_week_correct_answer():
    message_context = {
        "expected_answer": "Thursday",
        "message_body": "Thursday",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "Thursday"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_short_day_of_week_correct_answer_in_phrase():
    message_context = {
        "expected_answer": "Saturday",
        "message_body": "maybe they'd go on Sat",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "Saturday"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_short_day_of_week_wrong_answer():
    message_context = {
        "expected_answer": "Tuesday",
        "message_body": "mon",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "Monday"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_multiple_choice_correct_answer():
    message_context = {
        "expected_answer": "A",
        "message_body": "a",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "A"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_multiple_choice_wrong_answer():
    message_context = {
        "expected_answer": "D",
        "message_body": "That'd be C",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "C"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_multiple_choice_wrong_answer():
    message_context = {
        "expected_answer": "10",
        "message_body": "yep",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "out_of_scope"
    expected_nlu_response_data = "yep"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_multiple_choice_wrong_answer():
    message_context = {
        "expected_answer": "yes",
        "message_body": "sure",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "yes"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_multiple_choice_wrong_answer():
    message_context = {
        "expected_answer": "B",
        "message_body": "I want a hint",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "intent"
    expected_nlu_response_data = "math_question"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_yes_no_wrong_answer():
    message_context = {
        "expected_answer": "No",
        "message_body": "Yes",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "yes"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_true_false_wrong_answer():
    message_context = {
        "expected_answer": "F",
        "message_body": "T",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "T"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_wrong_answer_type_tf_mc_1():
    message_context = {
        "expected_answer": "T",
        "message_body": "C",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "C"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_wrong_answer_type_tf_mc_2():
    message_context = {
        "expected_answer": "F",
        "message_body": "D",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "D"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data
