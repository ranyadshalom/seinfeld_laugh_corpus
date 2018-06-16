from collections import Counter

from humor_recogniser.humor_recogniser import read_data


def run(data, output):
    screenplays = read_data(data)
    txt = screenplays_to_txt(screenplays)
    word_counts = count_words(txt)
    word_probabilities = calc_probabilities(word_counts)
    write_to_file(word_probabilities)
    # TODO take care of UNKs


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A script to calculate the probabilities of words occurring in a "
                                                 "screenplay.")
    parser.add_argument('data', help='The folder where the training data is located. Training data is .merged '
                                     'files, created by the data_merger.py module and contain screenplays, '
                                     'laugh times & dialog times.')
    parser.add_argument('output', help='Output file.')
    args = parser.parse_args()
    run(args.data, args.output)
