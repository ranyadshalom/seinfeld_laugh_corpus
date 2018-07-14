"""
By Ran Yad-Shalom
1.5.2018

Converts screenplays from seinfeldscripts.com to a single digestable format.
Format description:
CHARACTER\n - capitalized character name mean 'start dialog of this character', just as in standard screenplay format.
Regular text - spoken dialog.
INT. PLACE, TIME - a new scene.
# comment - Stage directions & parantheticals should be ignored by the parser, thus we will comment them out.
"""
import argparse
import re

delimiters_dict = {'(': ')',
                   '[': ']',
                   '<': '>'}
delimiters = set(d for d in (list(delimiters_dict.keys()) + list(delimiters_dict.values())))
scene_headings = ['INT.',
                  'EXT.',
                  '===',
                  '---']


def run(src, dst):
    with open(src, encoding='utf8', errors='ignore') as f:
        screenplay_as_str = f.read()

    result = reformat_screenplay(screenplay_as_str)
    print("Success! Writing to file '%s'..." % dst)

    with open(dst, 'w', encoding='utf8', errors='ignore') as f:
        f.write(result)


def get_words_generator(screenplay_as_str):
    for line in screenplay_as_str.split('\n'):
        yield '\n'
        for word in line.split():
            if word_has_parenthesis_inside(word):
                word_a, word_b = split_word_with_parenthesis(word)
                yield word_a
                yield word_b
            else:
                # break word and yield before and after delimiter
                # TODO solve this issue in the "process parenthesis" and "process character" combination
                yield word


def word_has_parenthesis_inside(word):
    proper_length = len(word) > 2
    has_delimiter = any((d in word[1:-1]) for d in delimiters)
    splitted = re.split("|".join("\\"+d for d in delimiters), word)
    is_letters = lambda w: any(c.isalpha() for c in w)
    has_ascii_after_split = all(is_letters(w) for w in splitted)

    return proper_length and has_delimiter and has_ascii_after_split


def split_word_with_parenthesis(word):
    for l in word:
        if delimiters_dict.get(l, ''):
            # left delimiter is inside the word
            return word.split(l)[0], l + word.split(l)[1]
        if l in delimiters_dict.values():
            # right delimiter is inside word
            return word.split(l)[0] + l, word.split(l)[1]


def process(words_generator):
    result = ""
    word = next(words_generator)
    while True:
        try:
            if word == '\n':
                result += word
                word = next(words_generator)
                if is_character(word):
                    # character can only appear after '\n'
                    block, word = process_character_block(word, words_generator)
                    result = result +  block + '\n'
            elif is_scene_heading(word):
                result = result[:-1] + process_scene_heading(word, words_generator)
                result += "\n** NEW SCENE **"
                word = next(words_generator)
            elif is_parenthesis(word):
                result += '\n' + process_parenthesis(word, words_generator)
                word = next(words_generator)
            elif is_comment(word):
                result += '\n' + process_scene_heading(word, words_generator)
                word = next(words_generator)
            else:
                result += word + ' '
                word = next(words_generator)
        except StopIteration:
            return result


def process_character_block(word, word_generator):
    block = process_character_name(word, word_generator)
    while True:
        word = next(word_generator)
        if is_parenthesis(word) or is_scene_heading(word):
           return block, word
        if word == '\n':
            return block, word
        else:
            block += (word + ' ')


def process_character_name(current_word, word_generator):
    try:
        while True:
            if current_word[-1] == ':':
                return current_word[:-1] + '\n'
            else:
                next_word = next(word_generator)
                if is_parenthesis(next_word):
                    return current_word + '\n' + process_parenthesis(next_word, word_generator)
                else:
                    return current_word + ' ' + process_character_name(next_word, word_generator)
    except StopIteration:
        raise ValueError("A character name did not end with ':' as expected. Please check screenplay.")


def process_parenthesis(word, word_generator, delimiter=None):
    """
    Process until you reach the right parenthesis. Turn to a comment.
    If you don't reach rhe right parenthesis, throw exception.
    """
    if not delimiter:
        delimiter = word[0]
        word = "# " + word
    try:
        if word[-1] == delimiters_dict.get(delimiter, ''):    # the dict returns the reverse delimiter, e.g. ')' for '('.
            return word + '\n'
        if word[-2] == delimiters_dict.get(delimiter, ''):
            return word[:-1] + '\n'
    except IndexError:
        pass    # 1 character words like 'I' or 'a'.

    try:
        return word + ' ' + process_parenthesis(next(word_generator), word_generator, delimiter)
    except StopIteration:
        raise ValueError("Parenthesis weren't closed as expected.\n"
                             "Delimiter: %s. Please check screenplay." % delimiter)


def process_scene_heading(word, word_generator):
    # process the whole line as a scene break.
    result = '# ' + word
    for word in word_generator:
        if word == '\n':
            break
        else:
            result += ' ' + word

    return result


def is_character(word):
    return word.isupper() and len(word) > 2 and word[:-1].replace(".", "").isalpha()


def is_scene_heading(word):
    return any(word.startswith(s) for s in scene_headings)


def is_parenthesis(word):
    return word[0] in delimiters_dict.keys()


def is_comment(word):
    return word[0] in ['%']


def reformat_screenplay(screenplay_as_str):
    """
    Try to think of the reformatted as a DFA. We scan the screenplay only once, while each word will be processed
    by a node according to the rules layed out before.
    :param screenplay_as_str:
    :return: a newly formatted screenplay
    """
    words_generator = get_words_generator(screenplay_as_str)
    word = next(words_generator)
    return process(words_generator)


if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Convert screenplays from seinfeldscripts.com to a single digestable format.")
    parser.add_argument('input', help='A .txt file of a seinfeld screenplay from seinfeldscripts.com')
    parser.add_argument('output', help='Destination .txt file.')
    args = parser.parse_args()
    src, dst = args.input, args.output

    run(src, dst)
