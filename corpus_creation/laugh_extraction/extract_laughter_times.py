import argparse
from numpy import mean, array_split, array, median, percentile, std
from math import sqrt
from scipy.io.wavfile import read
from collections import Counter

from corpus_creation.utils.utils import log10wrapper

db_measurement_chunks_per_second = 10           # chunks (to measure dB of) per second.
minimum_laughs = 85                             # if extracted less than this, something is wrong.


def run(input, output):
    dbs = get_audio_dbs(input)
    laughter_times = get_laughter_times(dbs)

    verify_result(laughter_times)
    write_to_file(laughter_times, output)


def get_audio_dbs(audio_file):
    """
    :param audio_file: The path to the episode's audio file.
    :return: an array of calculated dB measurements for the audio file.
    """
    samples_per_second, wavdata = read(audio_file, mmap=True)

    # split audio to chunks to measure Db
    numchunks = int((len(wavdata) / samples_per_second) * db_measurement_chunks_per_second)
    chunks = array_split(wavdata, numchunks)
    chunks = [array(chunk, dtype='int64') for chunk in chunks]      # to prevent integer overflow
    dbs = [20*log10wrapper( sqrt(mean(chunk**2)) ) for chunk in chunks]     # list of dB values for the chunks

    return dbs


def get_laughter_times(dbs):
    """
    :return: an array of the laugh timestamps in seconds.
    """
    silence_threshold = mean(dbs) - std(dbs)

    laughter_times = []
    for i in range(len(dbs)):
        s, fullness, m, result, mm = is_a_peak(dbs, i, silence_threshold)
        if result:
            total_seconds = i/db_measurement_chunks_per_second
            # minutes, seconds = int(total_seconds / 60), total_seconds % 60
            # print("%02d:%.1f LOL (std:%.3f, peak:%.3f, mean volume: %.3f, mean_without_peak: %.3f)" % (minutes, seconds, s, fullness, m, mm))
            laughter_times.append(total_seconds)
    return laughter_times


def is_a_peak(dbs, i, silence_threshold):
    rng = 3 * db_measurement_chunks_per_second

    try:
        if all(dB <= dbs[i] for dB in dbs[i:i+rng]) and all(dbs[i] >= dB for dB in dbs[i-rng:i]):
            # is a peak
            if mean(dbs[i-rng:i+rng]) > silence_threshold:
                std_of_interval = std(dbs[i-rng:i+rng])
                mean_of_interval = mean(dbs[i-rng:i+rng])
                if std_of_interval < mean_of_interval:
                    # usually when the standard deviation of the interval is bigger than the mean, it is a FP
                    return std_of_interval, dbs[i], mean_of_interval, True, mean(dbs[i-rng:i] + dbs[i+1:i + rng])
    except IndexError:
        return None, None, None, None, None
    return None, None, None, None, None


def verify_result(laughter_times):
    if len(laughter_times) < minimum_laughs:
        raise Exception("It seems like audience recording is not in Stereo (Only %d laughs were extracted)."
                        % len(laughter_times))


def write_to_file(laughter_times, output):
    with open(output, 'w') as f:
        f.write('# Time in which laughter occurs in the laugh track\n')
        for timestamp in laughter_times:
           f.write("{total_seconds} seconds ({minutes:02d}:{seconds:02d})\n".format(
               total_seconds = timestamp,
               minutes = int(timestamp / 60),
               seconds = int(timestamp % 60)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract laughter times (in seconds) in the laugh track")
    parser.add_argument('input', help='a laugh track (.wav, 44khz 16bit)')
    parser.add_argument('output', help="a plain text file with the laughter points")
    args = parser.parse_args()
    wav_file, output_file = args.input, args.output

    run(input=wav_file, output=output_file)
