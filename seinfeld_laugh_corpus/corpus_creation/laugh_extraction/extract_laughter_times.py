import argparse
import sys
from collections import namedtuple

from numpy import mean, array_split, array, median, std, sqrt, isinf
from scipy.io.wavfile import read

sys.path.insert(0, '..')
sys.path.insert(0, '.')

from corpus_creation.utils.utils import log10wrapper

Laugh = namedtuple('Laugh', ['time', 'vol'])
db_measurement_chunks_per_second = 10           # chunks (to measure dB of) per second.
minimum_laughs = 85                             # if extracted less than this, something is wrong.
minimum_laughter_dB = -44                       # if the volume of the laughters is less than this value, disqualify
minimum_standard_devation = 11                  # dB of the laugh track should have standard devation above this values.


def run(input, output):
    dbs = get_audio_dbs(input)
    laughters = get_laughters(dbs)
    verify_result(laughters, dbs)

    laughter_times = [l.time for l in laughters]
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
    dbs = [20*log10wrapper( mean(sqrt((chunk / 32767)**2)) ) for chunk in chunks]     # list of dB values for the chunks

    return dbs


def get_laughters(dbs):
    """
    :return: an array of the laugh timestamps in seconds.
    """
    dbs_without_infs = [dB for dB in dbs if not isinf(dB)]
    silence_threshold = mean(dbs_without_infs)
    m , s = median(dbs), std(dbs_without_infs)

    laughters = []
    for i in range(len(dbs)):
        s, fullness, m, result = is_a_peak(dbs, i, silence_threshold)
        if result:
            total_seconds = i/db_measurement_chunks_per_second
            #minutes, seconds = int(total_seconds / 60), total_seconds % 60
            #print("%02d:%.1f LOL (std:%.3f, peak:%.3f, mean volume: %.3f" % (minutes, seconds, s, fullness, m))
            laughters.append(Laugh(time=total_seconds, vol=m))
    return laughters


def is_a_peak(dbs, i, silence_threshold):
    detection_rng = 3 * db_measurement_chunks_per_second
    vol_measurement_rng = int(1 * db_measurement_chunks_per_second)

    try:
        if all(dB <= dbs[i] for dB in dbs[i:i+detection_rng]) and all(dbs[i] >= dB for dB in dbs[i-detection_rng:i]):
            # is a peak
            mean_of_interval = mean(dbs[i-vol_measurement_rng:i+vol_measurement_rng])
            if mean_of_interval > silence_threshold:
                std_of_interval = std(dbs[i-vol_measurement_rng:i+vol_measurement_rng])
                return std_of_interval, dbs[i], mean_of_interval, True
    except IndexError:
        return None, None, None, None
    return None, None, None, None


def verify_result(laughters, dbs):
    l_m = mean([l. vol for l in laughters])
    s = std(dbs)
    if l_m < minimum_laughter_dB:
        raise Exception("Laughter volume too low: %.3f. File may not be a proper laugh track." % l_m)
    if s < minimum_standard_devation:
        raise Exception("Standard deviation %.3f is too small (file does not have the shape of a laugh track)" % s)

    laughter_times = [l.time for l in laughters]
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