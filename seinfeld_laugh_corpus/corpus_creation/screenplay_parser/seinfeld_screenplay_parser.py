"""
By Ran Yad-Shalom
1.5.2018
"""

import argparse
import re

from .screenplay_parser import ScreenplayParser


def run(src, dst):
    p = SeinfeldScreenplayParser()
    p.to_file(src, dst)


class SeinfeldScreenplayParser(ScreenplayParser):
    """
    Specific implementation for screenplays from seinology.com.
    """
    delimiters_dict = {'(': ')',
                       '[': ']',
                       '<': '>'}
    delimiters = set(d for d in (list(delimiters_dict.keys()) + list(delimiters_dict.values())))
    scene_headings = ['INT.',
                      'EXT.',
                      '===',
                      '---']

    def _get_words_generator(self, screenplay_as_str):
        for line in screenplay_as_str.split('\n'):
            yield '\n'
            for word in line.split():
                if self._word_has_parenthesis_inside(word):
                    word_a, word_b = self._split_word_with_parenthesis(word)
                    yield word_a
                    yield word_b
                else:
                    # break word and yield before and after delimiter
                    # TODO solve this issue in the "process parenthesis" and "process character" combination
                    yield word

    def _word_has_parenthesis_inside(self, word):
        proper_length = len(word) > 2
        has_delimiter = any((d in word[1:-1]) for d in self.delimiters)
        splitted = re.split("|".join("\\"+d for d in self.delimiters), word)
        is_letters = lambda w: any(c.isalpha() for c in w)
        has_ascii_after_split = all(is_letters(w) for w in splitted)

        return proper_length and has_delimiter and has_ascii_after_split

    def _split_word_with_parenthesis(self, word):
        for l in word:
            if self.delimiters_dict.get(l, ''):
                # left delimiter is inside the word
                return word.split(l)[0], l + word.split(l)[1]
            if l in self.delimiters_dict.values():
                # right delimiter is inside word
                return word.split(l)[0] + l, word.split(l)[1]

    def _process(self, words_generator):
        result = ""
        word = next(words_generator)
        while True:
            try:
                if word == '\n':
                    result += word
                    word = next(words_generator)
                    if self._is_character(word):
                        # character can only appear after '\n'
                        block, word = self._process_character_block(word, words_generator)
                        result = result + block + '\n'
                elif self._is_scene_heading(word):
                    result = result[:-1] + self._process_scene_heading(word, words_generator)
                    result += "\n** NEW SCENE **"
                    word = next(words_generator)
                elif self._is_parenthesis(word):
                    result += '\n' + self._process_parenthesis(word, words_generator)
                    word = next(words_generator)
                elif self._is_comment(word):
                    result += '\n' + self._process_scene_heading(word, words_generator)
                    word = next(words_generator)
                else:
                    result += word + ' '
                    word = next(words_generator)
            except StopIteration:
                return result

    def _process_character_block(self, word, word_generator):
        block = self._process_character_name(word, word_generator)
        while True:
            word = next(word_generator)
            if self._is_parenthesis(word) or self._is_scene_heading(word):
               return block, word
            if word == '\n':
                return block, word
            else:
                block += (word + ' ')

    def _process_character_name(self, current_word, word_generator):
        try:
            while True:
                if current_word[-1] == ':':
                    return current_word[:-1] + '\n'
                else:
                    next_word = next(word_generator)
                    if self._is_parenthesis(next_word):
                        return current_word + '\n' + self._process_parenthesis(next_word, word_generator)
                    else:
                        return current_word + ' ' + self._process_character_name(next_word, word_generator)
        except StopIteration:
            raise ValueError("A character name did not end with ':' as expected. Please check screenplay.")

    def _process_parenthesis(self, word, word_generator, delimiter=None):
        """
        Process until you reach the right parenthesis. Turn to a comment.
        If you don't reach rhe right parenthesis, throw exception.
        """
        if not delimiter:
            delimiter = word[0]
            word = "# " + word
        try:
            if word[-1] == self.delimiters_dict.get(delimiter, ''):    # the dict returns the reverse delimiter, e.g. ')' for '('.
                return word + '\n'
            if word[-2] == self.delimiters_dict.get(delimiter, ''):
                return word[:-1] + '\n'
        except IndexError:
            pass    # 1 character words like 'I' or 'a'.

        try:
            return word + ' ' + self._process_parenthesis(next(word_generator), word_generator, delimiter)
        except StopIteration:
            raise ValueError("Parenthesis weren't closed as expected.\n"
                                 "Delimiter: %s. Please check screenplay." % delimiter)

    @staticmethod
    def _process_scene_heading(word, word_generator):
        # process the whole line as a scene break.
        result = '# ' + word
        for word in word_generator:
            if word == '\n':
                break
            else:
                result += ' ' + word

        return result

    @staticmethod
    def _is_character(word):
       return word.isupper() and len(word) > 2 and word[:-1].replace(".", "").isalpha()

    def _is_scene_heading(self, word):
        return any(word.startswith(s) for s in self.scene_headings)

    def _is_parenthesis(self, word):
        return word[0] in self.delimiters_dict.keys()

    @staticmethod
    def _is_comment(word):
        return word[0] in ['%']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert screenplays from seinfeldscripts.com to a single digestable format.")
    parser.add_argument('input', help='A .txt file of a seinfeld screenplay from seinfeldscripts.com')
    parser.add_argument('output', help='Destination .txt file.')
    args = parser.parse_args()
    src, dst = args.input, args.output

    run(src, dst)

