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


def simulate_api_call(client, student_message, expected_answer):
    message_data = add_message_text_to_sample_object(student_message, expected_answer)
    response = client.post("/v2/nlu", data=message_data)
    return response
