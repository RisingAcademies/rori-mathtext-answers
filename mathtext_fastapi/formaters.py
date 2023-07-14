def truncate_long_message_text(message_text):
    return message_text[0:100]


def format_single_event_nlu_response(
    eval_type,
    result,
    confidence=1,
    intents=[]
):
    """ Formats the result of a single event to the standard nlu response format

    Currently applies to comparison evaluation, timeout, and error responses
    
    >>> format_single_event_nlu_response('comparison', '25')
    {'type': 'comparison', 'data': '25', 'confidence': 1, 'intents': [{'type': 'comparison', 'data': '25', 'confidence': 1}, {'type': 'comparison', 'data': '25', 'confidence': 1}, {'type': 'comparison', 'data': '25', 'confidence': 1}]}
    """
    result_obj = {
        'type': eval_type,
        'data': result,
        'confidence': confidence,
    }

    intents = [
        result_obj.copy() for i in range(3)
    ]
    
    nlu_response = {
        'type': eval_type,
        'data': result,
        'confidence': confidence,
        'intents': intents,
    }
    return nlu_response
