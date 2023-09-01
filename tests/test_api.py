from fastapi.testclient import TestClient
import app

client = TestClient(app.app)
ENDPOINT = "/v2/nlu"


def add_message_text_to_sample_object(student_message, expected_answer):
    """
    Builds a sample request object using an example of a student answer

    Input
    - student_message: str - an example of user input to test
    - expected_answer: str - an example of the correct answer in the Rori spreadsheet

    Example Input
    "maybe 20", "20"

    Output
    - b_string: json b-string - simulated Turn.io message data

    Example Output
    b'{"message_data": {"author_id": "+3578931789", "author_type": "OWNER", "contact_uuid": "43qy76ga-4hjk-24nj-sfd7-k4ljl46j0ds09", "message_body": "test message", "message_direction": "inbound", "message_id": "4kl209sd0-a7b8-2hj3-8563-3hu4a89b32", "message_inserted_at": "2023-01-10T02:37:28.477940Z", "message_updated_at": "2023-01-10T02:37:28.487319Z"}}'

    """
    message_data = (
        "{"
        + f'"author_id": "+3578931789", "author_type": "OWNER", "contact_uuid": "43qy76ga-4hjk-24nj-sfd7-k4ljl46j0ds09", "message_body": "{student_message}", "expected_answer": "{expected_answer}", "message_direction": "inbound", "message_id": "4kl209sd0-a7b8-2hj3-8563-3hu4a89b32", "message_inserted_at": "2023-01-10T02:37:28.477940Z", "message_updated_at": "2023-01-10T02:37:28.487319Z"'
        + "}"
    )
    json_string = "{" + f'"message_data": {message_data}' + "}"
    b_string = json_string.encode("utf-8")

    return b_string


def simulate_api_call(student_message, expected_answer):
    message_data = add_message_text_to_sample_object(student_message, expected_answer)
    response = client.post(ENDPOINT, data=message_data)
    return response


def test_designate_correct_answer():
    response = simulate_api_call("10", "10")
    expected_nlu_response_type = "correct_answer"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type


def test_designate_wrong_answer():
    response = simulate_api_call("10", "15")
    expected_nlu_response_type = "wrong_answer"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type


def test_designate_correct_when_answer_in_phrase():
    response = simulate_api_call("maybe 2000", "2000")
    expected_nlu_response_type = "correct_answer"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type


def test_designate_wrong_when_answer_in_phrase():
    response = simulate_api_call("maybe 1000", "2000")
    expected_nlu_response_type = "wrong_answer"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type


def test_designate_correct_when_only_student_message_has_comma():
    response = simulate_api_call("3,000", "3000")
    expected_nlu_response_type = "correct_answer"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type


def test_designate_correct_when_only_expected_answer_has_comma():
    response = simulate_api_call("4000", "4,000")
    expected_nlu_response_type = "correct_answer"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type


def test_designate_out_of_scope_to_nonsense_utterance():
    response = simulate_api_call("maybe 2djkajdajk", "4,000")
    expected_nlu_response_type = "out_of_scope"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type


def test_designate_out_of_scope_to_irrelevant_utterance():
    response = simulate_api_call("Please send me data", "4,000")
    expected_nlu_response_type = "out_of_scope"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type


def test_designate_request_for_menu_as_intent():
    response = simulate_api_call("let me choose something else", "374")
    expected_nlu_response_type = "intent"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type


def test_designate_request_for_hint_as_intent():
    response = simulate_api_call("I need an explanation", "374")
    expected_nlu_response_type = "intent"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type


def test_designate_menu_as_keyword():
    response = simulate_api_call("menu", "374")
    expected_nlu_response_type = "keyword"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type


def test_designate_menu_misspelling_as_keyword():
    response = simulate_api_call("manu", "374")
    expected_nlu_response_type = "keyword"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type


def test_return_student_message_for_out_of_scope_data():
    response = simulate_api_call("dakjagjlkajlag", "22")
    expected_nlu_response_data = "dakjagjlkajlag"
    assert response.status_code == 200
    assert response.json()["data"] == expected_nlu_response_data


def test_return_number_for_correct_number_answer():
    response = simulate_api_call("twenty", "20")
    expected_nlu_response_data = "20"
    assert response.status_code == 200
    assert response.json()["data"] == expected_nlu_response_data


def test_return_number_for_wrong_number_answer():
    response = simulate_api_call("20", "25")
    expected_nlu_response_data = "20"
    assert response.status_code == 200
    assert response.json()["data"] == expected_nlu_response_data
