import os

from humor_recogniser.ml_humor_recogniser import read_data


def get():
    """
    :return:  The "Seinfeld" Corpus as a list of Screenplay objects.
    """
    corpus_path = os.path.join('the_corpus')
    return read_data(corpus_path)

