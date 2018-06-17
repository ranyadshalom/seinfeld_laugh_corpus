"""
All the features in this module will automatically be extracted by the FeatureExtractor object.
They must all receive a line and a context, and return a value.
"""
import re
from math import log

# load data required for the features
word_probabilities = {}
with open("data/word_prevalence.txt") as f:
    for line in f:
        word, prob = line.split()
        word_probabilities[word] = float(prob)


def num_of_words(line, context):
    """
    a temporary feature to test the design
    """
    return len(line.txt.split())


def character_speaking(line, context):
    return line.character


def word_prevalence(line, context):
    value = 0
    words = re.split(r'[\s\,\.\?\!\;\:"]', line.txt.lower())
    for word in words:
        if word:
            try:
                value += log(word_probabilities[word])
            except KeyError:
                value += log(word_probabilities['UNK'])
    return value



#def word_prevalence(line, context):
