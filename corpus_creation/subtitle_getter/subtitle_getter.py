import pysrt
import sys
from scipy.io.wavfile import read
from numpy import mean, array_split, array
from math import log10, sqrt

peak_detection_threshold = 100              # the amplitude difference between 2 sample points to be considered as a peak
db_measurement_chunks_per_second = 20       # chunks (to measure dB of) per second.


def run(episode_video, episode_audio, output):
    """
    not yet working!
    """
    extract_subtitles_from_mkv(episode_video, output)
    download_subtitles(episode_video, episode_audio, output)


def download_subtitles(episode_video, episode_audio, output, retry=0):
    """
    not yet working!
    """
    if retry > 4:
        print("ERROR downloading subtitles for '%s'." % episode_video)
        return

    # downloading code
    # if file exists, do not download.

    if not is_in_sync(output, episode_audio):
        # remove subtitle file
        return download_subtitles(episode_video, episode_audio, output, retry + 1)


def is_in_sync(subtitles, audio):
    """
    Checks if the subtitles match the audio.
    :param subtitles: path to an .srt file
    :param audio: path to the episode's .wav audio file.
    :return: False if not in sync OR 'subtitles' file doesn't exist.
    """
    subs = pysrt.open(subtitles, encoding='ansi ', error_handling='ignore')
    dbs = get_audio_db(audio)
    sync_threshold = 0.13   # percent of subtitles to have audio peaks for the subtitle file to be considered in sync
    # count how many subtitle starting times match actual peaks in the audio.
    peaks = 0
    for sub in subs:
        #print(sub.text)
        if is_a_peak((sub.start.ordinal / 1000), dbs):
            peaks += 1

    sync_measure = peaks / len(subs)
    print("'%s' subtitle/audio sync measure is: %.2f" % (audio.rsplit(".", 1)[0], sync_measure))
    return True if sync_measure > sync_threshold else False


def get_audio_db(audio_file):
    """

    :param audio_file:
    :return: an array of calculated dB for the audio file, with the resolution of
    """
    samples_per_second, wavdata = read(audio_file)

    # split audio to chunks to measure Db
    numchunks = int((len(wavdata) / samples_per_second) * db_measurement_chunks_per_second)
    chunks = array_split(wavdata, numchunks)
    chunks = [array(chunk, dtype='int64') for chunk in chunks]      # to prevent integer overflow
    dbs = [20*log10wrapper( sqrt(mean(chunk**2)) ) for chunk in chunks]     # list of dB values for the chunks

    return dbs


def log10wrapper(num):
    """
    :return: returns float_min instead of exception when given 0
    """
    if num == 0:
        return -float('inf')
    else:
        return log10(num)


def is_a_peak(sub_time, dbs):
    """
    :param sub_time: in seconds
    :param audio: numpy array of the audio samples
    :param samples_per_second:
    :return: True if it's a peak, False otherwise.
    """
    silence_threshold = 35
    talking_threshold = 45
    chunk_i = int(sub_time * db_measurement_chunks_per_second)

    silence = False
    for i in range(-5, 6):
        # print('%.2f' % dbs[chunk_i + i], end=' ')
        if dbs[chunk_i + i] < silence_threshold:
            silence = True
        elif dbs[chunk_i + i] >= talking_threshold and silence == True:
            silence = False
            return True     # is a peak

    # print("")
    return False    # not a peak


