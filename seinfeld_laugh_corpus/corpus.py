import os
import re

from seinfeld_laugh_corpus.humor_recogniser.ml_humor_recogniser import read_data


class Corpus:
    """
    A container class for the whole corpus.
    """

    def __init__(self, screenplays):
        self.screenplays = screenplays
        self.screenplays_dict = {}
        for screenplay in screenplays:
            self.screenplays_dict[(screenplay.season, screenplay.episode)] = screenplay

    def __iter__(self):
        for screenplay in self.screenplays:
            yield screenplay

    def __getitem__(self, key):
        """
        :param key: a string with the season number and episode number, for instance 's04e05'.
        :return: The requested episode.
        """
        if isinstance(key, tuple):
            return self.screenplays_dict[key]
        elif isinstance(key, int):
            return self.screenplays[key]
        else:
            raise KeyError

    def search(self, query):
        """
        Search an episode by name.
        :param query: the episode's name.
        :return: The requested episode, if it exists.
        """
        query_bow = set(re.split(r'[\s\,\.\?\!\;\:"]', query.lower()))

        max_match = 0
        result = None
        for screenplay in self.screenplays_dict.values():
            screenplay_bow = set(re.split(r'[\s\,\.\?\!\;\:"]', screenplay.episode_name.lower()))
            match = len(screenplay_bow & query_bow)
            if match > max_match:
                max_match = match
                result = screenplay

        print("Found episode: '%s'" % str(result))
        return result


def load(fold_laughs=False):
    """
    :param fold_laughs: When set to True, screenplays will not contain Laugh objects. A line's funniness will still be
                        accessible via the "is_funny" attribute. The laughter time (in seconds) is stored in a line's
                        "laugh_time" attribute.
    :return:  The "Seinfeld" Corpus as a list of Screenplay objects.
    """
    corpus_path = os.path.join(os.path.dirname(__file__), 'the_corpus')
    screenplays = read_data(corpus_path, fold_laughs)
    corpus = Corpus(screenplays)
    return corpus
