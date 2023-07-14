from mathtext.constants import TOKENS2INT_ERROR_INT

def build_single_event_nlu_response(
    eval_type,
    result,
    confidence=1,
    intents=[]
):
    """ Formats the result of a single event to the standard nlu response format

    Currently applies to comparison evaluation, timeout, and error responses
    
    >>> build_single_event_nlu_response('comparison', '25')
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


def build_evaluation_response_object(
    results,
    evals=['text_extraction', 'regex_answer_extraction', 'number_extraction', 'intents']
):
    nlu_response = {
        'type': 'error',
        'data': TOKENS2INT_ERROR_INT,
        'confidence': 0,
        'intents': results.get('intents', [])
    }

    for eval in evals:
        if results.get(eval):
            nlu_response['type'] = eval

            if isinstance(results[eval], dict):
                try:
                    nlu_response['data'] = results[eval].get('result', '')
                    nlu_response['confidence'] = results[eval].get('confidence', 0)
                    return nlu_response
                except:
                    continue
            if isinstance(results[eval], list):
                try:
                    nlu_response['data'] = results['intents'][0]['data']
                    nlu_response['confidence'] = results['intents'][0]['confidence']
                    return nlu_response
                except:
                    break
    return nlu_response
