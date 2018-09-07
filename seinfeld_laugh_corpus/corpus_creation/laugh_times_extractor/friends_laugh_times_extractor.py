import argparse
import sys
from collections import namedtuple

from numpy import mean, array_split, array, median, std, sqrt, isinf
from scipy.io.wavfile import read

from seinfeld_laugh_corpus.corpus_creation.laugh_times_extractor.laugh_times_extractor import LaughTimesExtractor


def run(input, output):
    laugh_times_extractor = FriendsLaughTimesExtractor()
    laugh_times_extractor.to_file(input, output)


class FriendsLaughTimesExtractor(LaughTimesExtractor):
    silence = -80   # in dB
    min_theme_song_length_in_seconds = 34
    max_theme_song_length_in_seconds = 50

    def _detect_and_cut_out_theme_song(self, dbs):
        """
        The 'friends' theme song is recorded in Stereo and thus confuses our LaughTimesExtractor module.
        This method detects it.
        :param dbs: an array of dB values corresponding to the episode's volume in consecutive times. The exact
                    units per second division is in the parent class.
        :return: None (adjusts the dbs array)
        """
        m = mean([dB for dB in dbs if not isinf(dB)])
        min_theme_song_length = self.min_theme_song_length_in_seconds * self.db_measurement_chunks_per_second
        max_theme_song_length = self.max_theme_song_length_in_seconds * self.db_measurement_chunks_per_second

        k = 0
        for i, dB in enumerate(dbs):
            if dB >= m:
                k += 1
            else:
                if min_theme_song_length <= k <= max_theme_song_length:
                    print("'Friends' theme song detected from %.2d:%.2d to %.2d:%.2d - Silencing it." %
                          (self._get_minutes_and_seconds((i - k) / self.db_measurement_chunks_per_second) +
                           self._get_minutes_and_seconds(i / self.db_measurement_chunks_per_second)))
                    while k != 0:
                        dbs[i - k] = self.silence
                        k -= 1
                    break
                k = 0

    @staticmethod
    def _get_minutes_and_seconds(seconds):
        return int(seconds / 60), seconds % 60

    def _get_audio_dbs(self, audio_file):
        dbs = super()._get_audio_dbs(audio_file)
        self._detect_and_cut_out_theme_song(dbs)
        return dbs


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract laughter times (in seconds) in the laugh track")
    parser.add_argument('input', help='a laugh track (.wav, 44khz 16bit)')
    parser.add_argument('output', help="a plain text file with the laughter points")
    args = parser.parse_args()
    wav_file, output_file = args.input, args.output

    run(input=wav_file, output=output_file)
