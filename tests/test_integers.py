from fastapi.testclient import TestClient
from tests.simulate_api_call import simulate_api_call
import app

client = TestClient(app.app)


def test_designate_correct_answer():
    message_context = {
        "expected_answer": "10",
        "message_body": "10",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "10"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_designate_wrong_answer():
    message_context = {
        "expected_answer": "15",
        "message_body": "10",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "10"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_designate_correct_when_answer_in_phrase():
    message_context = {
        "expected_answer": "2000",
        "message_body": "maybe 2000",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "2000"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_designate_wrong_when_answer_in_phrase():
    message_context = {
        "expected_answer": "2000",
        "message_body": "maybe 1000",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "1000"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_designate_correct_when_only_student_message_has_comma():
    message_context = {
        "expected_answer": "3000",
        "message_body": "3,000",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "3000"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_designate_correct_when_only_expected_answer_has_comma():
    message_context = {
        "expected_answer": "4,000",
        "message_body": "4000",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "4,000"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_return_number_for_correct_number_answer():
    message_context = {
        "expected_answer": "20",
        "message_body": "twenty",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "20"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_return_number_for_wrong_number_answer():
    message_context = {
        "expected_answer": "25",
        "message_body": "20",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "20"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_equivalent_decimal_against_integer():
    message_context = {
        "expected_answer": "101",
        "message_body": "101.0",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "101"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_equivalent_integer_against_decimal_for_yes_confusion():
    message_context = {
        "expected_answer": "1.0",
        "message_body": "1",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "1.0"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_equivalent_integer_against_decimal():
    message_context = {
        "expected_answer": "17.0",
        "message_body": "17",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "17.0"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_wrong_integer_against_decimal():
    message_context = {
        "expected_answer": "1.0",
        "message_body": "1.1",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "1.1"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_wrong_decimal_against_integer():
    message_context = {
        "expected_answer": "101",
        "message_body": "102.0",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "102.0"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


# Note: For now commas are stripped from the result
def test_wrong_answer_with_comma():
    message_context = {
        "expected_answer": "1839",
        "message_body": "1,455",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "1455"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_right_answer_with_comma_in_student_message():
    message_context = {
        "expected_answer": "123496",
        "message_body": "123,496",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "123496"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_right_answer_with_comma_in_expected_answer():
    message_context = {
        "expected_answer": "123,496",
        "message_body": "123496",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "123,496"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_right_answer_with_comma_in_wrong_position():
    message_context = {
        "expected_answer": "123496",
        "message_body": "12,3496",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "123496"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_period_substitute_for_comma_fails():
    message_context = {
        "expected_answer": "80,005",
        "message_body": "80.005",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "80.005"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_period_substitute_for_comma_fails_2():
    message_context = {
        "expected_answer": "13",
        "message_body": "1.3",
    }
    response = simulate_api_call(client, message_context)
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "1.3"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data
