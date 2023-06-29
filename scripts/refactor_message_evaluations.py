import copy
import datetime
import pandas as pd
import re

# Only used for simulated_evaluation function
KEYWORDS = [
    'easier',
    'exit',
    'harder',
    'hint',
    'next',
    'stop',
    'tired',
    'tomorrow',
    'finished',
    'help',
    'easy',
    'support',
    'skip',
    'menu'
]


APPROVED_RESPONSE_CASES = [
    ['yes', 'answer', ['yes', 't']],
    ['y', 'answer', ['yes', 't']],
    ['yah', 'answer', ['yes', 't']],
    ['yeah', 'answer', ['yes',  't']],
    ['ok', 'answer', ['yes', 't']],
    ['okay', 'answer', ['yes', 't']],
    ['okey', 'answer', ['yes', 't']],
    ['yea', 'answer', ['yes', 't']],
    ['yh', 'answer', ['yes', 't']],
    ['ys', 'answer', ['yes', 't']],
    ['yrs', 'answer', ['yes', 't']],
    ['yes.', 'answer', ['yes', 't']],
    ['yep', 'answer', ['yes', 't']],
    ['yee', 'answer', ['yes', 't']],
    ['yed', 'answer', ['yes', 't']],
    ['yesh', 'answer', ['yes', 't']],
    ['yew', 'answer', ['yes', 't']],
    ['yex', 'answer', ['yes', 't']],
    ['yey', 'answer', ['yes', 't']],
    ['yez', 'answer', ['yes', 't']],
    ['ready', 'answer', ['yes']],
    ['proceed', 'answer', ['yes']],
    ['continue', 'answer', ['yes']],
    ['t', 'answer', ['yes', 't']],
    ['true', 'answer', ['yes', 't']],
    ['1', 'answer', ['yes', 't']],
    ['no', 'answer', ['no', 'f']],
    ['n', 'answer', ['no', 'f']],
    ['nah', 'answer', ['no', 'f']],
    ['f', 'answer', ['no', 'f']],
    ['false', 'answer', ['no', 'f']],
    ['0', 'answer', ['no', 'f']],
    ['even', 'answer', ['even']],
    ['odd', 'answer', ['odd']],
    ['monday', 'answer', ['monday']],
    ['tuesday', 'answer', ['tuesday']],
    ['wednesday', 'answer', ['wednesday']],
    ['thursday', 'answer', ['thursday']],
    ['friday', 'answer', ['friday']],
    ['saturday', 'answer', ['saturday']],
    ['sunday', 'answer', ['sunday']],
    ['mon', 'answer', ['monday']],
    ['tues', 'answer', ['tuesday']],
    ['wed', 'answer', ['wednesday']],
    ['thurs', 'answer', ['thursday']],
    ['fri', 'answer', ['friday']],
    ['sat', 'answer', ['saturday']],
    ['sun', 'answer', ['sunday']],
    ['>', 'answer', ['>', 'g']],
    ['g', 'answer', ['>', 'g']],
    ['gt', 'answer', ['>', 'g']],
    ['greater', 'answer', ['>', 'g']],
    ['greater than', 'answer', ['>', 'g']],
    ['<', 'answer', ['<', 'l']],
    ['l', 'answer', ['<', 'l']],
    ['lt', 'answer', ['<', 'l']],
    ['less', 'answer', ['<', 'l']],
    ['less than', 'answer', ['<', 'l']],
    ['>=', 'answer', ['>=', 'gte']],
    ['gte', 'answer', ['>=', 'gte']],
    ['greater than or equal', 'answer', ['>=', 'gte']],
    ['<=', 'answer', ['<=', 'lte']],
    ['lte', 'answer', ['<=', 'lte']],
    ['less than or equal', 'answer', ['<=', 'lte']],
    ['=', 'answer', ['=', 'e']],
    ['e', 'answer', ['=', 'e']],
    ['equal', 'answer', ['=', 'e']],
    ['same', 'answer', ['=', 'e']],
    ['a', 'answer', ['a']],
    ['b', 'answer', ['b']],
    ['c', 'answer', ['c']],
    ['d', 'answer', ['d']],
    ['easier', 'keyword', 'easier'],
    ['harder', 'keyword', 'harder'],
    ['hint', 'keyword', 'hint'],
    ['next', 'keyword', 'next'],
    ['stop', 'keyword', 'stop'],
    ['help', 'keyword', 'help'],
    ['support', 'keyword', 'support'],
    ['skip', 'keyword', 'skip'],
    ['menu', 'keyword', 'menu'],
    # These keywords below may not be very useful
    ['finish', 'keyword', 'finish'],
    ['hard', 'keyword', 'hard'],
    ['tired', 'keyword', 'tired'],
    ['tomorrow', 'keyword', 'tomorrow'],
    ['finished', 'keyword', 'finished'],
    ['exit', 'keyword', 'exit'],
    ['easy', 'keyword', 'easy'],
    ['manu', 'keyword', 'menu'],
    ['menue', 'keyword', 'menu'],
    ['meun', 'keyword', 'menu'],
    ['menus', 'keyword', 'menu'],
    ['skip', 'keyword', 'menu'],
    ['hints', 'keyword', 'menu']
]

APPROVED_RESPONSES_BY_TYPE = {}
KEYWORD_LOOKUP = {}
TEXT_ANSWER_LOOKUP = {}
for entry in APPROVED_RESPONSE_CASES:
    APPROVED_RESPONSES_BY_TYPE[entry[0]] = entry[1]
    if entry[1] == 'answer':
        TEXT_ANSWER_LOOKUP[entry[0]] = entry[2]
    else:
        KEYWORD_LOOKUP[entry[0]] = entry[2]

NUMBER_MAP = {
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
    'ten': 10,
    'eleven': 11,
    'twelve': 12,
    'thirteen': 13,
    'fourteen': 14,
    'fifteen': 15,
    'sixteen': 16,
    'seventeen': 17,
    'eighteen': 18,
    'nineteen': 19,
    'twenty': 20,
    'thirty': 30,
    'forty': 40,
    'fourty': 40,
    'fifty': 50,
    'sixty': 60,
    'seventy': 70,
    'eighty': 80,
    'ninety': 90,
    'hundred': 100,
    'thousand': 1000,
    'million': 1000000,
    'billion': 1000000000,
    'trillion': 1000000000000,
}


def regex_evaluation(normalized_student_message):
    """
    >>> regex_evaluation('it's 11:30')
    11:30
    >>> regex_evaluation('maybe 1/2')
    '1/2'
    """
    try:
        timestamp = datetime.datetime.strptime(normalized_student_message[3:-1], '%H:%M:%S')
        text = timestamp.strftime('%H:%M')
    except ValueError:
        text = normalized_student_message
    patterns = [
        r'\b\d{1,2}\s*:\s*\d{2}\b', # time
        r'[-]?\d+(\.\d+)?\s*\^\s*[-]?\d+(\.\d+)?', # exponent
        r'(\d+\s+)?\d+\s*/\s*\d+', # fraction
        r"\d+\s*?\.\s*?\d+" # decimal
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            normalized_response = re.sub(r'\s', "", match.group(0))
            return normalized_response


def normalize_message_and_answer(student_message, expected_answer):
    """
    >>> normalize_message_and_answer("Maybe 5000", "5,000")
    "maybe 5000", "5000"
    >>> normalize_message_and_answer("Yeah I think so", "Yes)
    "yeah I think so", "yes"
    """
    normalized_student_message = str(student_message).strip().replace(',','').lower()[0:100] 
    normalized_expected_answer = str(expected_answer).strip().replace(',','').lower()
    return normalized_student_message, normalized_expected_answer


def extract_approved_response_from_phrase(
    tokenized_student_message,
    normalized_expected_answer,
    expected_answer
):
    """
    >>> extract_approved_response_from_phrase(['maybe', 'y'], 'yes', 'Yes')   
    Yes
    >>> extract_approved_response_from_phrase(['*menu*', 'y'], 'yes', 'Yes')   
    menu
    >>> extract_approved_response_from_phrase(['maybe', '5000'], '5000', '5000')   
    None
    """
    answer_dict = copy.deepcopy(APPROVED_RESPONSES_BY_TYPE)
    if not answer_dict.get(normalized_expected_answer,''):
        answer_dict[normalized_expected_answer] = 'expected_answer'
    answer_types = [(answer_dict[token.replace('.', '').replace('*','')], token.replace('.', '').replace('*','')) for token in tokenized_student_message if token.replace('.', '').replace('*','') in answer_dict]

    for answer_type in answer_types:
        if answer_type[0] == 'expected_answer':
            return expected_answer
    for answer_type in answer_types:
        if answer_type[0] == 'answer' and normalized_expected_answer in TEXT_ANSWER_LOOKUP[answer_type[1]]:
            return expected_answer
    for answer_type in answer_types:
        if answer_type[0] == 'keyword':
            return KEYWORD_LOOKUP[answer_type[1]]


def is_number(normalized_student_message):
    """
    >>> is_number("maybe 5000")
    False
    >>> is_number("2")
    True
    >>> is_number("2.75")
    True
    >>> is_number("-3")
    True
    """
    try:
        if float(normalized_student_message):
            return True
    except ValueError:
        pass
    try:
        if int(normalized_student_message):
            return True
    except ValueError:
        pass
    return False


def is_answer_type_different(
    normalized_student_message, normalized_expected_answer
):
    """
    >>> is_answer_type_different("2", "B")
    True
    >>> is_answer_type_different("2", "2.5")
    False
    >>> is_answer_type_different("B", "Yes")
    True
    """
    is_num_student_message = is_number(normalized_student_message)
    is_text_student_message = normalized_student_message in TEXT_ANSWER_LOOKUP
    is_num_expected_answer = is_number(normalized_student_message)
    is_text_expected_answer = normalized_expected_answer in TEXT_ANSWER_LOOKUP

    if is_num_student_message and is_text_expected_answer or is_text_student_message and is_num_expected_answer:
        return True
    return False


def extract_numbers_with_regex(
    normalized_student_message,
    normalized_expected_answer,
    expected_answer
):
    """
    >>> extract_numbers_with_regex("maybe 5000", "5000", 5,000")
    '5,000'
    >>> extract_numbers_with_regex("maybe it's 2.5 or 3.5", "5", "5")
    None
    >>> extract_numbers_with_regex("maybe", "5", "5")
    None
    """
    result = re.search(r"\d+(?:\.\d+)?|\d", normalized_student_message)  
    is_num_expected_answer = is_number(normalized_expected_answer)
    if is_num_expected_answer and result:
        if result[0] == normalized_expected_answer:
            print(f"result: success")
            return expected_answer
        

def refactored_evaluations(student_message, expected_answer):
    result = ''
    normalized_student_message, normalized_expected_answer= normalize_message_and_answer(student_message, expected_answer)

    if normalized_student_message.replace(' ', '') == normalized_expected_answer.replace(' ', ''):
        return expected_answer

    tokenized_student_message = normalized_student_message.split()

    extracted_approved_response = extract_approved_response_from_phrase(
        tokenized_student_message,
        normalized_expected_answer,
        expected_answer
    )
    if extracted_approved_response:
        return extracted_approved_response

    result = regex_evaluation(normalized_student_message)
    if result:
        return result

    result = extract_numbers_with_regex(
        normalized_student_message,
        normalized_expected_answer,
        expected_answer
    )
    if result:
        return result

    result = [NUMBER_MAP[token] for token in tokenized_student_message if token in NUMBER_MAP]
    if result:
        if str(sum(result)) == normalized_expected_answer:
            return expected_answer





def simulate_evaluation(spreadsheet='rori_student_responses.xlsx'):
    """
    Runs the evaluation function on the spreadsheet from Owen
    """
    df = pd.read_excel(spreadsheet)

    total_cases = 0
    evaluation_matches = 0

    results = []
    for index, row in df.iterrows():
        total_cases += 1
        student_message = row['text']
        expected_answer = row['expected_answer']
        is_correct_answer = row['student_answer_correct']

        evaluation_result = refactored_evaluations(student_message, expected_answer)

        results.append([
            student_message,
            expected_answer,
            is_correct_answer,
            evaluation_result
        ])

        if (evaluation_result and is_correct_answer == 'correct') or (evaluation_result in KEYWORDS) or (evaluation_result == expected_answer):
            evaluation_matches += 1
    
    results_df = pd.DataFrame(
        results,
        columns=[
            'Student Message',
            'Expected Answer',
            'is_correct_answer',
            'Evaluation Result'
        ])
    results_df.to_csv('test_results.csv', index=False)

    print("RESULTS=================")
    print(f"Total Cases: {total_cases}")
    print(f"Evaluation Matches: {evaluation_matches}")

simulate_evaluation()

