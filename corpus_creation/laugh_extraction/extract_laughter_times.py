import argparse

# package imports
from scipy.io.wavfile import read

silence_threshold, trigger_threshold = 2, 150
detection_interval = 0.05                       # in seconds
minimum_laughs = 50                             # if extracted less than this, something is wrong.

def run(input, output):
    samples_per_second, data = read(input)
    focus_size = int(detection_interval * samples_per_second)

    laughter_times = get_laughter_times(data, focus_size, samples_per_second)
    verify_result(laughter_times)
    write_to_file(laughter_times, output)


def get_laughter_times(data, focus_size, samples_per_second):
    """
    :return: an array of the laugh timestamps in seconds.
    """
    laughter_times = []
    before_silence = False
    i = 0

    while i < len(data):
        value = abs(data[i][0])
        if value > trigger_threshold and before_silence:
            #   if the signal is loud in the next 10 samples, this is a laughter.
            if all(((abs(data[j][0]) > trigger_threshold) for j in range(i,i + focus_size*10, focus_size))):
                laughter_times.append(i / samples_per_second)
                i += (focus_size * 10)
                before_silence = False
        elif value < silence_threshold:
            before_silence = True
        i += focus_size

    return laughter_times


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