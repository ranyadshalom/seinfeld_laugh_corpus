"""
This module is not operational. Sorry.


All the features in this module will automatically be extracted by the FeatureExtractor object.
They must all receive a line and a context, and return a value.
"""
import re
import os
from math import log
import nltk
#import en_core_web_md
#from nltk.sentiment.vader import SentimentIntensityAnalyzer

# load word probabilities
#word_probabilities = {}
#
#word_prevalence_path = os.path.join(os.path.dirname(__file__), 'data', 'word_prevalence.txt')
#with open(word_prevalence_path) as f:
#    for line in f:
#        word, prob = line.split()
#        word_probabilities[word] = float(prob)
#

def _extract_full_correspondence_from_context(line, context):
    # TODO maybe the context should only be BACKWARDS!
    this_dialog_line = ''
    previous_dialog_line = ''
    try:
        seperators = []
        for i in range(len(context)-1):
            if context[i].character != context[i+1].character:
                seperators.append(i+1)

        this_dialog_line = context[seperators[-1]:]
        this_dialog_line = " ".join(l.txt for l in this_dialog_line)
        previous_dialog_line = context[seperators[-2]:seperators[-1]]
        previous_dialog_line = " ".join(l.txt for l in previous_dialog_line)
    except IndexError:
         pass
    return previous_dialog_line, this_dialog_line


def num_of_words(line, context):
    """
    a temporary feature to test the design
    """
    return [('num_of_word', len(line.txt.split()))]


def character_speaking(line, context):
    return [('character_speaking', line.character)]

#
#def word_prevalence(line, context):
#    value = 0
#    words = re.split(r'[\s\,\.\?\!\;\:"]', line.txt.lower())
#    for word in words:
#        if word:
#            try:
#                value += log(word_probabilities[word])
#            except KeyError:
#                value += log(word_probabilities['UNK'])
#    return [('word_prevalence', value)]
#
#
#def rarest_word_probability(line, context):
#    words = re.split(r'[\s\,\.\?\!\;\:"]', line.txt.lower())
#    words = [word for word in words if word]
#    line_word_probabilities = [word_probabilities[word] for word in words if word in word_probabilities]
#    if not line_word_probabilities:
#        line_word_probabilities.append(0)
#    return [('rarest_word_probability', min(line_word_probabilities))]
#
#
#def sentiment_and_semantical_differences(line, context):
#    # sentiments
#    prev_dialog, this_dialog = _extract_full_correspondence_from_context(line, context)
#    sid = SentimentIntensityAnalyzer()
#    prev_dialog_ss = sid.polarity_scores(prev_dialog)
#    this_dialog_ss = sid.polarity_scores(this_dialog)
#
#    # semantic similarity
#    doc1, doc2 = nlp(this_dialog), nlp(prev_dialog)
#    return [('vader_sent_prev_dialog_neg', prev_dialog_ss['neg']),
#            ('vader_sent_prev_dialog_neu', prev_dialog_ss['neu']),
#            ('vader_sent_prev_dialog_pos', prev_dialog_ss['pos']),
#            ('vader_sent_prev_dialog_comp', prev_dialog_ss['compound']),
#            ('vader_sent_dialog_neg', this_dialog_ss['neg']),
#            ('vader_sent_dialog_neu', this_dialog_ss['neu']),
#            ('vader_sent_dialog_pos', this_dialog_ss['pos']),
#            ('vader_sent_dialog_comp', this_dialog_ss['compound']),
#            ('semantical_similarity', doc1.similarity(doc2))
#            ]
#
#
#
#def word_prevalence(line, context):
