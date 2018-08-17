import argparse
import re
import sys
from collections import Counter

sys.path.append("..")

from ml_humor_recogniser import read_data
from screenplay import Line


def run(data, output):
    screenplays = read_data(data)
    txt = screenplays_to_txt(screenplays)
    word_counts = get_word_counts(txt)
    word_probabilities = get_probabilities(word_counts)
    write_to_file(word_probabilities, output)
    # TODO take care of UNKs


def screenplays_to_txt(screenplays):
    result = ''
    for screenplay in screenplays:
        for line in screenplay:
            if isinstance(line, Line):
                result += ('\n' + line.txt)
    return result


def get_word_counts(txt):
    """
    Counts word occurrences in "txt".
    The methodology of dealing with unknown words is to calculate a count of "UNK" by splitting the set of words, and
    after counting words in the bigger set, every unknown word that appears in the smaller set will be counted as "UNK".
    :param txt:
    :return: a {'word':integer} dictionary that represents the number of times a word appears in the txt.
    """
    counts = Counter()
    all_words = re.split(r'[\s\,\.\?\!\;\:"]', txt.lower())
    all_words = [w for w in all_words if w]
    size = len(all_words)
    most_words, rest = all_words[:int(size*0.9)], all_words[int(size*0.9):]

    for word in most_words:
        counts[word] += 1
    for word in rest:
        if word in counts:
            counts[word] += 1
        else:
            counts['UNK'] += 1

    return counts


def get_probabilities(word_counts):
    probabilities = {}
    total_num_of_words = sum((count for _, count in word_counts.items()))
    for word in word_counts.keys():
        probabilities[word] = word_counts[word] / total_num_of_words

    return probabilities


def write_to_file(word_probabilities, output):
    with open(output, 'w') as f:
        for word, prob in word_probabilities.items():
            f.write("%s %.9f\n" % (word, prob))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A script to calculate the probabilities of words occurring in a "
                                                 "screenplay.")
    parser.add_argument('data', help='The folder where the training data is located. Training data is .merged '
                                     'files, created by the data_merger.py module and contain screenplays, '
                                     'laugh times & dialog times.')
    parser.add_argument('output', help='Output file.')
    args = parser.parse_args()
    run(args.data, args.output)
