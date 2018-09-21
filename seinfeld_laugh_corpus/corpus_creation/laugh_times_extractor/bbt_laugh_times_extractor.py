import argparse
import sys
from collections import namedtuple

from numpy import mean, array_split, array, median, std, sqrt, isinf
from scipy.io.wavfile import read

from seinfeld_laugh_corpus.corpus_creation.laugh_times_extractor.friends_laugh_times_extractor import FriendsLaughTimesExtractor


def run(input, output):
    laugh_times_extractor = BbtLaughTimesExtractor()
    laugh_times_extractor.run(input, output)


class BbtLaughTimesExtractor(FriendsLaughTimesExtractor):
    min_theme_song_length_in_seconds = 18
    max_theme_song_length_in_seconds = 25


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract laughter times (in seconds) in the laugh track")
    parser.add_argument('input', help='a laugh track (.wav, 44khz 16bit)')
    parser.add_argument('output', help="a plain text file with the laughter points")
    args = parser.parse_args()
    wav_file, output_file = args.input, args.output

    run(input=wav_file, output=output_file)
