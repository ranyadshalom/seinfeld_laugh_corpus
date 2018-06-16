"""
All the features in this module will automatically be extracted by the FeatureExtractor object.
They must all receive a line and a context, and return a value.
"""


def num_of_words(line, context):
    """
    a temporary feature to test the design
    """
    return len(line.txt.split())


def character_speaking(line, context):
    return line.character

#def word_prevalence(line, context):
