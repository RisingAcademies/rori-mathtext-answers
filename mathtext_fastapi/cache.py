import json
import os
import redis
import functools
from mathtext_fastapi.constants import REDIS_RESPONSE_CACHE_URL

from logging import getLogger
log = getLogger(__name__)

r = redis.StrictRedis.from_url(
    REDIS_RESPONSE_CACHE_URL
)


def create_hash_key(function_name, function_input):
    """ Creates a hash key describing the object inputs
    https://redis.io/docs/data-types/tutorial/ 

    Note: Not all functions use the expected_answer
    """
    given_answer = function_input[0]
    expected_answer = function_input[1] if len(function_input) == 2 else None

    given_answer_str = f"given_answer:{given_answer}"
    expected_answer_str = ''
    if expected_answer:
        expected_answer = f":expected_answer:{expected_answer}"
    hash_key = f"{function_name}:{given_answer_str}{expected_answer_str}"
    return hash_key


def check_redis(hash_key, input):
    """ Checks if the user input has an existing key in the cache

    Returns the cache item if found or None if not found
    """
    try:
        if r.exists(hash_key):
            # Gets the result if it exists
            result = r.get(hash_key)
            return json.loads(result)
    except redis.exceptions.RedisError as e:
        log.error(f'Redis failed during look up: {e}')
    return None


def add_to_redis(hash_key, input, result):
    """ Adds the an unstored nlu response object to the cache """
    try:
        r.set(hash_key, json.dumps(result))
    except redis.exceptions.RedisError as e:
        log.error(f'Redis failed during write: {e} / {result}')
        return False
    return True


def get_or_create_redis_entry(function_name):
    def decorator(func):
        """ A decorator function that handles using and caching the function result """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # args: positional arguments
            # kwargs: keyword arguments
            func_input = args
            hash_key = create_hash_key(function_name, func_input)

            # Examine the cache and return the result
            redis_result = check_redis(hash_key, func_input)
            if redis_result:
                # print(f"Redis Result: {redis_result}")
                return redis_result

            # Run the actual function
            result = func(*args, **kwargs)

            # Update the cache with a new value
            add_to_redis(hash_key, func_input, result)
            # print(f"New Result: {result}")

            # Return the decorated function's result
            return result
        # Signifies the completion of the decorator itself
        # Decorator replaces the decorated function
        return wrapper
    return decorator