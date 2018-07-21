import pysrt
import re
import requests
import os
import subprocess
import ntpath
import gzip
from scipy.io.wavfile import read
from numpy import mean, array_split, array
from math import log10, sqrt
from pythonopensubtitles.opensubtitles import OpenSubtitles

from corpus_creation.config import opensubtitles_credentials, FFMPEG_PATH

peak_detection_threshold = 100            # the amplitude difference between 2 sample points to be considered as a peak
db_measurement_chunks_per_second = 20     # chunks (to measure dB of) per second.

ost = OpenSubtitles()
ost_token = ost.login(opensubtitles_credentials['user'], opensubtitles_credentials['password'])


def run(episode_video, episode_audio, output):
    try:
        if not os.path.exists(output):
            extract_subtitles_from_mkv(episode_video, output)
        else:
            print("Using the existing subtitles file.")
        if is_in_sync(output, episode_audio):
            return
        else:
            print("Subtitles from .mkv file are not in sync! trying to download...")
    except Exception as e:
        print("Couldn't extract subtitles from .mkv! (%s)\n"
              "Make sure you have a working version of ffmpeg in the external_tools folder.\n"
              "trying to download them..." % str(e))

    fetch_subtitles_from_opensubtitles(episode_video, episode_audio, output)


def extract_subtitles_from_mkv(episode_video, output):
    # ffmpeg will extract the subtitles from the .mkv file.
    exit_code = subprocess.call([os.path.join(FFMPEG_PATH, 'ffmpeg.exe'), "-i", episode_video, '-map', '0:s:0',
                                 output], stdout=subprocess.DEVNULL)
    if exit_code != 0:
        raise Exception("ffmpeg exit code: %d. Subtitles could not be extracted. Please make sure"
                        "that the .mkv file contains text subtitles and not bitmap subtitles." % exit_code)


def fetch_subtitles_from_opensubtitles(episode_video_path, episode_audio, output):
    episode_video = ntpath.basename(episode_video_path)
    max_retries = 5
    # downloading code
    m = re.findall(r'\d+', episode_video)
    se, ep = int(m[0]), int(m[1])
    results = ost.search_subtitles([{'query': 'Seinfeld',
                                     'episode': ep,
                                     'season': se,
                                     'sublanguageid': 'eng'}])

    for result in results[:max_retries]:
        try:
            download_subtitle(result, output)
            if is_in_sync(output, episode_audio):
                print("Found a subtitle that is in sync: %s" % result['SubFileName'])
                return
        except Exception as e:
            print("ERROR download sutitle '%s': %s" % (result['SubFileName'], str(e)))
            pass

    raise Exception("Out of %d opensubtitles results, none of them are in sync!" % len(results))


def download_subtitle(result, output):
    url = result['SubDownloadLink']
    res = requests.get(url)
    if res.status_code != 200:
        raise Exception("server returned %d: %s" % (res.status_code, res.reason))
    content = gzip.decompress(res.content)
    with open(output, 'w', encoding='utf8', errors='ignore') as f:
        f.write(content)


def is_in_sync(subtitles, audio):
    """
    Checks if the subtitles match the audio.
    :param subtitles: path to an .srt file
    :param audio: path to the episode's .wav audio file.
    :return: False if not in sync OR 'subtitles' file doesn't exist.
    """
    subs = pysrt.open(subtitles, encoding='ansi ', error_handling='ignore')
    dbs = get_audio_db(audio)
    sync_threshold = 0.05   # percent of subtitles to have audio peaks for the subtitle file to be considered in sync
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
    samples_per_second, wavdata = read(audio_file, mmap=True)

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
            return True     # is a peak

    # print("")
    return False    # not a peak


class SubtitlesNotInSyncException(Exception):
    pass
