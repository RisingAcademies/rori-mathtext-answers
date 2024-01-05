import json
import random


def make_random_author_id():
    random_number = random.randint(1000000000, 9999999999)
    return "+" + str(random_number)


def add_message_text_to_sample_object(message_context):
    """
    Builds a sample request object configured with the message_dict values

    Input
    - message_context: dict - key value pairs to update the default message data with

    Example Input
    - {"student_answer": "maybe 20", "expected_answer": "20"}

    Output
    - b_string: json b-string - simulated Turn.io message data

    Example Output
    b'{"message_data": {"author_id": "+3578931789", "author_type": "OWNER", "contact_uuid": "43qy76ga-4hjk-24nj-sfd7-k4ljl46j0ds09", "message_body": "test message", "message_direction": "inbound", "message_id": "4kl209sd0-a7b8-2hj3-8563-3hu4a89b32", "message_inserted_at": "2023-01-10T02:37:28.477940Z", "message_updated_at": "2023-01-10T02:37:28.487319Z"}}'

    """

    default_message_values = {
        # Contact
        "author_id": make_random_author_id(),
        "author_type": "OWNER",
        "contact_uuid": "43qy76ga-4hjk-24nj-sfd7-k4ljl46j0ds09",
        "user_attempts": "1",
        # Microlesson
        "question_micro_lesson": "G1.N1.1.1.1",
        "question_level": "1",
        "question_skill": "Test API Skill",
        "question_topic": "Test API Topic",
        "question": "___, 27, 28, 29, 30",
        "question_number": "5",
        "expected_answer": "1",
        # Message
        "message_body": "0",
        "message_direction": "inbound",
        "message_id": "4kl209sd0-a7b8-2hj3-8563-3hu4a89b32",
        "message_inserted_at": "2023-01-10T02:37:28.477940Z",
        "message_updated_at": "2023-01-10T02:37:28.487319Z",
        # Context
        "line_number": "+12065906259",
        "line_name": "Local Testing",
    }

    default_message_values.update(message_context)
    message_dict_converted = json.dumps(default_message_values)
    json_string = "{" + f'"message_data": {message_dict_converted}' + "}"
    b_string = json_string.encode("utf-8")

    return b_string


def simulate_api_call(client, message_context):
    message_data = add_message_text_to_sample_object(message_context)
    response = client.post("/v2/nlu", data=message_data)
    return response
