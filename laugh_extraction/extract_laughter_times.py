import argparse

# package imports
from scipy.io.wavfile import read

silence_threshold, trigger_threshold = 2, 150
detection_interval = 0.05                          # in seconds



def run(input, output):
    samples_per_second, data = read(input)
    focus_size = int(detection_interval * samples_per_second)

    laughter_times = get_laughter_times(data, focus_size)
    write_to_file(laughter_times, output)


def get_laughter_times(data, focus_size):
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
                laughter_times.append(i / 44100)
                i += (focus_size * 10)
                before_silence = False
        elif value < silence_threshold:
            before_silence = True
        i += focus_size

    return laughter_times


def write_to_file(laughter_times, output):
    with open(output, 'w') as f:
        f.write('# Time in which laughter occurs in the laugh track\n')
        for timestamp in laughter_times:
           f.write("{total_seconds} seconds ({minutes:02d}:{seconds:02d})\n".format(
               total_seconds = timestamp,
               minutes = int(timestamp / 60),
               seconds = int(timestamp % 60)))


if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Extract laughter times (in seconds) in the laugh track")
    parser.add_argument('input', help='a laugh track (.wav, 44khz 16bit)')
    parser.add_argument('output', help="a plain text file with the laughter points")
    args = parser.parse_args()
    wav_file, output_file = args.input, args.output

    run(input=wav_file, output=output_file)
