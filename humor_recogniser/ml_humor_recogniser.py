"""
A machine-learning based classifier that tries to guess which lines in a Seinfeld script will trigger the audience's
laughter.

Written by Ran Yad-Shalom
"""

# python imports
import os
import argparse
import logging
from sklearn import linear_model
from sklearn.feature_extraction import DictVectorizer

# project imports
from humor_recogniser.screenplay import Screenplay
from humor_recogniser.feature_extractor import FeatureExtractor

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

feature_extractor = FeatureExtractor()
vec = DictVectorizer()


def run(data_folder):
    data = read_data(data_folder)

    test_size = int(len(data) * 0.2)
    train_set, test_set = data[test_size:], data[:test_size]

    classifier = get_classifier(train_set)
    test_classifier(test_set, classifier)


def read_data(data_folder):
    data = []
    files = (f for f in os.listdir(data_folder) if os.path.isfile(data_folder + '/' + f))

    for file in files:
        try:
            screenplay = Screenplay.from_file("%s/%s" % (data_folder, file))
            data.append(screenplay)
        except Exception as e:
            print("ERROR incompatible data file '%s'. Skipped. (%s)" % (file, e))
    return data


def get_classifier(train_set):
    X, Y = [], []

    for screenplay in train_set:
        for x, y in feature_extractor.yield_features(screenplay):
            X.append(x)
            Y.append(y)
    classifier = linear_model.LogisticRegression()
    classifier.fit(vec.fit_transform(X).toarray(), Y)
    return classifier


def test_classifier(test_set, classifier):
    # test classifier
    stats = {'tp': 0, 'fp': 0, 'tn': 0, 'fn': 0}
    for screenplay in test_set:
        for x, y in feature_extractor.yield_features(screenplay):
            if classifier.predict(vec.transform(x).toarray()) == 'funny':
                if y == 'funny':
                    stats['tp'] += 1
                else:
                    stats['fp'] += 1
            else:   # classifier prediction was 'not_funny'
                if y == 'not_funny':
                    stats['tn'] += 1
                else:
                    stats['fn'] += 1

    print_statistics(stats)


def print_statistics(stats):
    tp, fp, tn, fn = stats['tp'], stats['fp'], stats['tn'], stats['fn']
    try:
        precision = tp / (tp+fp)
    except ZeroDivisionError:
        precision = 0

    try:
        recall = tp / (tp+fn)
    except ZeroDivisionError:
        recall = 0

    logger.info("Accuracy: %.2f" % ((tn+tp) / (tn+tp+fn+fp)))
    logger.info("Precision: %.2f" % precision)
    logger.info("Recall: %.2f" % recall)
#   logger.info("F1: %.2f" % (2*(precision*recall)/(precision+recall)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A machine-learning based module that to predict the times in which "
                                                 "the crowd laughter occurs given a Seinfeld screenplay.")
    parser.add_argument('data', help='The folder where the training data is located. Training data is .merged '
                                            'files, created by the data_merger.py module and contain screenplays, '
                                            'laugh times & dialog times.')
    args = parser.parse_args()
    run(args.data)

# THIS SECTION CAN BE IGNORED FOR THE WHILE AS IT MAINLY CONSISTS OF NOTES TO SELF, THOUGHTS AND PONDERING.
# WRITING IT ALL DOWN HELPS ME MAKE DECISIONS AND REACH CONCLUSIONS.

# Text-based feature idea list:
#
#   * The character that speaks
#   * The character that last spoke
#   * How many sentences ago the last character spoke / how many subtitles ago the last character spoke
#   * The last sentence (simplified - sentiment score, semantic value [based on word2vec])
#   * This sentence (simplified)
#   * Language model (try a bunch of them, and even generate one if needs) value of this sentence.
#   *

# Time-based feature idea list:
# NOTE TO SELF: THESE FEATURES ARE NOT BINARY! You've never worked with such features before. Please make sure you're
#               doing it right, lest they will be utterly meaningless (no joke has the exact same timing data).
#
#   * How long it took to say this sentence considering the number of syllables (longer-lingering sentences maye funnier?)
#   * How much SILENCE do we have before the joke? (this might be a good indicator, but it is not always available).
#   *

# Possible problems and solutions:
#   Q: How to deal with a sentence that's spread across 2 subtitles and more?
#   A: Don't need to. It almost never happens (can count exactly how many times in all my data to demonstrate this point)

#   Q: Not all sentences / dialog lines have timestamps, since sometimes 2 characters' sentences are spread across
#      one subtitle. How should I deal with that?
#   A: It's just gonna be left out of the feature vector... it's OK...


# A laugh could only appear in the data after a subtitle. Thus the decision has to be made
# after each subtitle.
