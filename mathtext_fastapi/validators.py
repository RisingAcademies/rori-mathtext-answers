import datetime as dt
from collections.abc import Mapping
from dateutil.parser import isoparse
from json import JSONDecodeError
from logging import getLogger

from mathtext_fastapi.constants import ERROR_RESPONSE_DICT

log = getLogger(__name__)

PAYLOAD_VALUE_TYPES = {
    'author_id': str,
    'author_type': str,
    'contact_uuid': str,
    'message_body': str,
    'message_direction': str,
    'message_id': str,
    'message_inserted_at': str,
    'message_updated_at': str,
    }


def payload_is_valid(payload_object):
    """
    >>> payload_is_valid({'author_id': '+5555555', 'author_type': 'OWNER', 'contact_uuid': '3246-43ad-faf7qw-zsdhg-dgGdg', 'message_body': 'thirty one', 'message_direction': 'inbound', 'message_id': 'SDFGGwafada-DFASHA4aDGA', 'message_inserted_at': '2022-07-05T04:00:34.03352Z', 'message_updated_at': '2023-04-06T10:08:23.745072Z'})
    True

    >>> payload_is_valid({"author_id": "@event.message._vnd.v1.chat.owner", "author_type": "@event.message._vnd.v1.author.type", "contact_uuid": "@event.message._vnd.v1.chat.contact_uuid", "message_body": "@event.message.text.body", "message_direction": "@event.message._vnd.v1.direction", "message_id": "@event.message.id", "message_inserted_at": "@event.message._vnd.v1.chat.inserted_at", "message_updated_at": "@event.message._vnd.v1.chat.updated_at"})
    False
    """
    try:
        isinstance(
            isoparse(payload_object.get('message_inserted_at', '')),
            dt.datetime
        )
        isinstance(
            isoparse(payload_object.get('message_updated_at', '')),
            dt.datetime
        )
    except ValueError:
        return False
    return (
        isinstance(payload_object, Mapping) and
        isinstance(payload_object.get('author_id'), str) and
        isinstance(payload_object.get('author_type'), str) and
        isinstance(payload_object.get('contact_uuid'), str) and
        isinstance(payload_object.get('message_body'), str) and
        isinstance(payload_object.get('message_direction'), str) and
        isinstance(payload_object.get('message_id'), str) and
        isinstance(payload_object.get('message_inserted_at'), str) and
        isinstance(payload_object.get('message_updated_at'), str)
    )


def log_payload_errors(payload_object):
    errors = []
    try:
        assert isinstance(payload_object, Mapping)
    except Exception as e:
        log.error(f'Invalid HTTP request payload object: {e}')
        errors.append(e)
    for k, typ in PAYLOAD_VALUE_TYPES.items():
        try:
            assert isinstance(payload_object.get(k), typ)
        except Exception as e:
            log.error(f'Invalid HTTP request payload object: {e}')
            errors.append(e)
    try:
        assert isinstance(
            dt.datetime.fromisoformat(
                payload_object.get('message_inserted_at')
            ),
            dt.datetime
        )
    except Exception as e:
        log.error(f'Invalid HTTP request payload object: {e}')
        errors.append(e)
    try:
        isinstance(
            dt.datetime.fromisoformat(
                payload_object.get('message_updated_at')
            ),
            dt.datetime
        )
    except Exception as e:
        log.error(f'Invalid HTTP request payload object: {e}')
        errors.append(e)
    return errors


async def parse_nlu_api_request_for_message(request):
    """ Extracts the message data from a request sent to the /nlu endpoint """
    try:
        payload = await request.json()
    except JSONDecodeError as e:
        log.info(f'JSONDecodeError: {e}')
        return ERROR_RESPONSE_DICT
    
    message_dict = payload.get('message_data')
    log.info(f'Request json: {payload}')

    if not message_dict:
        message_dict = payload.get('message', {})

    if not payload_is_valid(message_dict):
        log_payload_errors(message_dict)
        return ERROR_RESPONSE_DICT
    return message_dict 