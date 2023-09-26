from fastapi.testclient import TestClient
from tests.simulate_api_call import simulate_api_call
import app

client = TestClient(app.app)


def test_designate_menu_as_keyword():
    response = simulate_api_call(client, "menu", "374")
    expected_nlu_response_type = "keyword"
    expected_nlu_response_data = "menu"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_designate_menu_misspelling_as_keyword():
    response = simulate_api_call(client, "manu", "374")
    expected_nlu_response_type = "keyword"
    expected_nlu_response_data = "menu"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_designate_help_as_keyword():
    response = simulate_api_call(client, "help", "374")
    expected_nlu_response_type = "keyword"
    expected_nlu_response_data = "help"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_designate_stop_as_keyword():
    response = simulate_api_call(client, "stop", "374")
    expected_nlu_response_type = "keyword"
    expected_nlu_response_data = "stop"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_designate_next_as_keyword():
    response = simulate_api_call(client, "next", "374")
    expected_nlu_response_type = "keyword"
    expected_nlu_response_data = "next"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data


def test_designate_support_as_keyword():
    response = simulate_api_call(client, "support", "374")
    expected_nlu_response_type = "keyword"
    expected_nlu_response_data = "support"
    assert response.status_code == 200
    assert response.json()["type"] == expected_nlu_response_type
    assert response.json()["data"] == expected_nlu_response_data
