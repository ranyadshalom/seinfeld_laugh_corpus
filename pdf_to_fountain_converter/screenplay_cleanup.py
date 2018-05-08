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
from io import StringIO

delimiters_dict = {'(': ')',
                   '[': ']',
                   '<': '>'}
scene_headings = ['INT.',
                  'EXT.']

# Rules:
# 1. If starts with a word is all caps, enter charcacter mode untill you see the :.  else throw parsing error.
#
# that ends with :, it's a starting point of a dialog.
#       then read dialog untill...
#           One of the other rules comes up
# 2. If it starts with [,< - it's a stage direction. comment.
# 3. if it starts with -- and is quite long, it might be a scene break.
# 4. comment whenever not in dialog mode!
# 5. If one of these expressions is in this line, it's a new scene (Commercial break, New scene,
#       TODO can't be a new scene more than once in a row...


def run(src, dst):
    with open(src, encoding='utf8') as f:
        screenplay_as_str = f.read()

    result = reformat_screenplay(screenplay_as_str)
    print("Success! Writing to file '%s'..." % dst)

    with open(dst, 'w', encoding='utf8') as f:
        f.write(result)


def get_words_generator(screenplay_as_str):
    for line in screenplay_as_str.split('\n'):
        yield '\n'
        for word in line.split():
            yield word


def process(words_generator):
    result = ""
    word = next(words_generator)
    while True:
        try:
            if word == '\n':
                result += word
                word = next(words_generator)
            if is_scene_heading(word):
                result = result[:-1] + process_scene_heading(word, words_generator)
                result += "\n** NEW SCENE **"
                word = next(words_generator)
            elif is_character(word):
                block, word = process_character_block(word, words_generator)
                result = result[:-1] +  block
            elif is_parenthesis(word):
                result += '\n' + process_parenthesis(word, words_generator)
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
        if is_parenthesis(word) or is_character(word) or is_scene_heading(word):
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
                    return current_word + process_parenthesis(next_word, word_generator) + process_character_name(next(word_generator), word_generator)
                else:
                    return current_word + process_character_name(next_word, word_generator)
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
    return (word.isupper() and len(word) > 3 and word[:-1].isalpha())

def is_scene_heading(word):
    return any(word.startswith(s) for s in scene_headings)

def is_parenthesis(word):
    return word[0] in delimiters_dict.keys()



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
