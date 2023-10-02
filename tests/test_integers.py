from fastapi.testclient import TestClient
from tests.simulate_api_call import simulate_api_call
import app

client = TestClient(app.app)


def test_designate_correct_answer():
    response = simulate_api_call(client, "10", "10")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "10"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_designate_wrong_answer():
    response = simulate_api_call(client, "10", "15")
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "10"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_designate_correct_when_answer_in_phrase():
    response = simulate_api_call(client, "maybe 2000", "2000")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "2000"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_designate_wrong_when_answer_in_phrase():
    response = simulate_api_call(client, "maybe 1000", "2000")
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "1000"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_designate_correct_when_only_student_message_has_comma():
    response = simulate_api_call(client, "3,000", "3000")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "3000"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_designate_correct_when_only_expected_answer_has_comma():
    response = simulate_api_call(client, "4000", "4,000")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "4,000"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_return_number_for_correct_number_answer():
    response = simulate_api_call(client, "twenty", "20")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "20"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_return_number_for_wrong_number_answer():
    response = simulate_api_call(client, "20", "25")
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "20"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_equivalent_decimal_against_integer():
    response = simulate_api_call(client, "101.0", "101")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "101"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_equivalent_integer_against_decimal_for_yes_confusion():
    response = simulate_api_call(client, "1", "1.0")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "1.0"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_equivalent_integer_against_decimal():
    response = simulate_api_call(client, "17", "17.0")
    expected_nlu_response_type = "correct_answer"
    expected_nlu_response_data = "17.0"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_wrong_integer_against_decimal():
    response = simulate_api_call(client, "1.1", "1.0")
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "1.1"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_wrong_decimal_against_integer():
    response = simulate_api_call(client, "102.0", "101")
    expected_nlu_response_type = "wrong_answer"
    expected_nlu_response_data = "102.0"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data
