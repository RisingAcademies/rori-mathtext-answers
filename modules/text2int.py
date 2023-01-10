import spacy  # noqa

# import os
# os.environ['KMP_DUPLICATE_LIB_OK']='True'
# import spacy

# Change this according to what words should be corrected to
SPELL_CORRECT_MIN_CHAR_DIFF = 2

TOKENS2INT_ERROR_INT = 32202

ONES = [
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "seventeen", "eighteen", "nineteen",
]

CHAR_MAPPING = {
    "-": " ",
    "_": " ",
    "and": " ",
}
# CHAR_MAPPING.update((str(i), word) for i, word in enumerate([" " + s + " " for s in ONES]))
TOKEN_MAPPING = {
    "and": " ",
    "oh": "0",
}


def find_char_diff(a, b):
    # Finds the character difference between two str objects by counting the occurences of every character. Not edit distance.
    char_counts_a = {}
    char_counts_b = {}
    for char in a:
        if char in char_counts_a.keys():
            char_counts_a[char] += 1
        else:
            char_counts_a[char] = 1
    for char in b:
        if char in char_counts_b.keys():
            char_counts_b[char] += 1
        else:
            char_counts_b[char] = 1
    char_diff = 0
    for i in char_counts_a:
        if i in char_counts_b.keys():
            char_diff += abs(char_counts_a[i] - char_counts_b[i])
        else:
            char_diff += char_counts_a[i]
    return char_diff


def tokenize(text):
    text = text.lower()
    # print(text)
    text = replace_tokens(''.join(i for i in replace_chars(text)).split())
    # print(text)
    text = [i for i in text if i != ' ']
    # print(text)
    output = []
    for word in text:
        # print(word)
        output.append(convert_word_to_int(word))
    output = [i for i in output if i != ' ']
    # print(output)
    return output


def detokenize(tokens):
    return ' '.join(tokens)


def replace_tokens(tokens, token_mapping=TOKEN_MAPPING):
    return [token_mapping.get(tok, tok) for tok in tokens]


def replace_chars(text, char_mapping=CHAR_MAPPING):
    return [char_mapping.get(c, c) for c in text]


def convert_word_to_int(in_word, numwords={}):
    # Converts a single word/str into a single int
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
    scales = ["hundred", "thousand", "million", "billion", "trillion"]
    if not numwords:
        for idx, word in enumerate(ONES):
            numwords[word] = idx
        for idx, word in enumerate(tens):
            numwords[word] = idx * 10
        for idx, word in enumerate(scales):
            numwords[word] = 10 ** (idx * 3 or 2)
    if in_word in numwords:
        # print(in_word)
        # print(numwords[in_word])
        return numwords[in_word]
    try:
        int(in_word)
        return int(in_word)
    except ValueError:
        pass
    # Spell correction using find_char_diff
    char_diffs = [find_char_diff(in_word, i) for i in ONES + tens + scales]
    min_char_diff = min(char_diffs)
    if min_char_diff <= SPELL_CORRECT_MIN_CHAR_DIFF:
        return char_diffs.index(min_char_diff)


def tokens2int(tokens):
    # Takes a list of tokens and returns a int representation of them
    types = []
    for i in tokens:
        if i <= 9:
            types.append(1)

        elif i <= 90:
            types.append(2)

        else:
            types.append(3)
    # print(tokens)
    if len(tokens) <= 3:
        current = 0
        for i, number in enumerate(tokens):
            if i != 0 and types[i] < types[i - 1] and current != tokens[i - 1] and types[i - 1] != 3:
                current += tokens[i] + tokens[i - 1]
            elif current <= tokens[i] and current != 0:
                current *= tokens[i]
            elif 3 not in types and 1 not in types:
                current = int(''.join(str(i) for i in tokens))
                break
            elif '111' in ''.join(str(i) for i in types) and 2 not in types and 3 not in types:
                current = int(''.join(str(i) for i in tokens))
                break
            else:
                current += number

    elif 3 not in types and 2 not in types:
        current = int(''.join(str(i) for i in tokens))

    else:
        """
        double_list = []
        current_double = []
        double_type_list = []
        for i in tokens:
            if len(current_double) < 2:
                current_double.append(i)
            else:
                double_list.append(current_double)
                current_double = []
        current_double = []
        for i in types:
            if len(current_double) < 2:
                current_double.append(i)
            else:
                double_type_list.append(current_double)
                current_double = []
        print(double_type_list)
        print(double_list)
        current = 0
        for i, type_double in enumerate(double_type_list):
            if len(type_double) == 1:
                current += double_list[i][0]
            elif type_double[0] == type_double[1]:
                current += int(str(double_list[i][0]) + str(double_list[i][1]))
            elif type_double[0] > type_double[1]:
                current += sum(double_list[i])
            elif type_double[0] < type_double[1]:
                current += double_list[i][0] * double_list[i][1]
        #print(current)
        """
        count = 0
        current = 0
        for i, token in enumerate(tokens):
            count += 1
            if count == 2:
                if types[i - 1] == types[i]:
                    current += int(str(token) + str(tokens[i - 1]))
                elif types[i - 1] > types[i]:
                    current += tokens[i - 1] + token
                else:
                    current += tokens[i - 1] * token
                count = 0
            elif i == len(tokens) - 1:
                current += token

    return current


def text2int(text):
    # Wraps all of the functions up into one
    return tokens2int(tokenize(text))
