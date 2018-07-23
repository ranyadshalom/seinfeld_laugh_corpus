import argparse
from numpy import mean, array_split, array, median, percentile, std
from math import sqrt
from scipy.io.wavfile import read

from corpus_creation.utils.utils import log10wrapper

db_measurement_chunks_per_second = 5            # chunks (to measure dB of) per second.
minimum_laughs = 80                             # if extracted less than this, something is wrong.


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
    lenght_in_seconds = int(len(dbs) / db_measurement_chunks_per_second)

    samples_mean = mean(dbs)
    standard_deviation = std(dbs)
    for (second, chunk) in enumerate(array_split(dbs, lenght_in_seconds)):
        # each chunk represents 1 second of audio
        minutes, seconds = int(second / 60), int(second % 60)
        print("%02d:%02d - " % (minutes, seconds), end='')
        for dB in chunk:
            print("%.2f" % dB, end=' ')
        if any(dB > samples_mean + standard_deviation for dB in chunk):
            print("LOL")
        print("")
    return [] # TODO count laughs


def is_a_peak(dbs, i):
    m = 10

    for dt in range(2,20):
        i_mean = mean(dbs[i:i+dt])
        left_mean = mean(dbs[i-dt:i])
        right_mean = mean(dbs[i+dt:i+2*dt])
        if i_mean - left_mean > m and i_mean - right_mean > m:
            print("LOL")


def verify_result(laughter_times):
    if len(laughter_times) < minimum_laughs:
        raise Exception("It seems like audience recording is not in Stereo (Only %d laughs were extracted)."
                        % len(laughter_times))
    # TODO verify spillage (the average silence levels? First see if this is even a problem.)


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
