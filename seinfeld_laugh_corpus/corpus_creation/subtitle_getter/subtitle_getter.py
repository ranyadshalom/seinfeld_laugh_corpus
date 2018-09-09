import gzip
import ntpath
import os
import re
import subprocess
import sys
from time import sleep

import pysrt
import requests
from numpy import mean, array_split, array, std, sqrt, isinf
from pythonopensubtitles.opensubtitles import OpenSubtitles
from scipy.io.wavfile import read

sys.path.insert(0, '..')
sys.path.insert(0, '.')

from corpus_creation.config import opensubtitles_credentials, FFMPEG_PATH
from corpus_creation.utils.utils import log10wrapper

peak_detection_threshold = 100          # the amplitude difference between 2 sample points to be considered as a peak
db_measurement_chunks_per_second = 20   # chunks (to measure dB of) per second.
ost_retry = 60                          # number of seconds to wait before retrying to connect to opensubtitles.
sync_threshold = 0.094                  # A float between 0 to 1. The higher the number, the more in-sync the subtitles.


def run(episode_video, episode_audio, output):
    dbs = get_audio_dbs(episode_audio)
    try:
        if not os.path.exists(output):
            extract_subtitles_from_mkv(episode_video, output)
        else:
            print("Using the existing subtitles file.")
        if is_valid(output, dbs):
            return
        else:
            print("Subtitles from .mkv file are not in valid! trying to download...")
    except Exception as e:
        print("Couldn't extract subtitles from .mkv! (%s)\n"
              "Make sure you have a working version of ffmpeg in the external_tools folder.\n"
              "trying to download them..." % str(e))

    fetch_subtitles_from_opensubtitles(episode_video, dbs, output)


def extract_subtitles_from_mkv(episode_video, output):
    # ffmpeg will extract the subtitles from the .mkv file.
    exit_code = subprocess.call([os.path.join(FFMPEG_PATH, 'ffmpeg.exe'), "-i", episode_video, '-map', '0:s:0',
                                 output], stdout=subprocess.DEVNULL)
    if exit_code != 0:
        raise Exception("ffmpeg exit code: %d. Subtitles could not be extracted. Please make sure"
                        "that the .mkv file contains text subtitles and not bitmap subtitles." % exit_code)


def fetch_subtitles_from_opensubtitles(episode_video_path, dbs, output):
    max_results = 5
    results = get_opensubtitles_search_results(episode_video_path)
    best_result = {'sync_measure': 0}

    for result in results[:max_results]:
        try:
            download_subtitle(result, output)
            print("Checking if subtitle '%s' is in sync..." % result['SubFileName'])
            subs = pysrt.open(output, encoding='ansi ', error_handling='ignore')
            result['sync_measure'] = get_sync_measure(subs, dbs)
            if result['sync_measure'] > best_result['sync_measure'] and has_enough_dashes(subs):
                best_result = result
        except Exception as e:
            print("ERROR downloading subtitle '%s': %s" % (result['SubFileName'], str(e)))
            pass

    if best_result['sync_measure'] > sync_threshold:
        print("Downloading best synced subtitle...")
        download_subtitle(best_result, output)
        return

    raise Exception("Out of %d opensubtitles results, none of them are valid!" % len(results[:max_results]))


def get_opensubtitles_search_results(episode_video_path):
    ost = get_open_subtitles_object()
    episode_video = ntpath.basename(episode_video_path)
    retry = 60
    # downloading code
    m = re.findall(r'\d+', episode_video)
    se, ep = int(m[0]), int(m[1])
    while True:
        try:
            results = ost.search_subtitles([{'query': 'Seinfeld',
                                             'episode': ep,
                                             'season': se,
                                             'sublanguageid': 'eng'}])
        except Exception as e:
            print("Error getting search results from 'opensubtitles'. retrying in %d seconds..." % retry)
            sleep(retry)
            retry *= 2
        else:
            return results


def get_open_subtitles_object():
    """
    :return: a logged-in OpenSubtitles object.
    """
    ost = OpenSubtitles()
    try:
        ost_token = ost.login(opensubtitles_credentials['user'], opensubtitles_credentials['password'])
    except Exception as e:
        print("ERROR getting Opensubtitles token: %s.\n Retrying in %d seconds..." % (str(e), ost_retry))
        sleep(ost_retry)
        ost_retry *= 2  # exponential backoff
    return ost


def download_subtitle(result, output):
    retry = 0
    interval = 60

    url = result['SubDownloadLink']
    while True:
        res = requests.get(url)
        if res.status_code != 200:
            if retry < 3:
                print("Server returned %d: %s. Retrying in %d seconds..." % (res.status_code, res.reason, interval))
                retry += 1
                sleep(interval)
                interval *= 2
            else:
                raise Exception("ERROR: server returned %d: %s" % (res.status_code, res.reason))
        else:
            break
    content = gzip.decompress(res.content)
    with open(output, 'wb') as f:
        f.write(content)


def is_valid(subtitles, dbs):
    """
    Checks the validity of the subtitles.
    :param subtitles: the path to the .srt subtitle file.
    :param dbs: an array of the dB audio levels.
    :return: True if they're valid, False otherwise.
    """
    subs = pysrt.open(subtitles, encoding='ansi ', error_handling='ignore')

    if not has_enough_dashes(subs):
        print("Subtitles don't have enough dashes. Dropping them.")
        return False
    if get_sync_measure(subs, dbs) < sync_threshold:
        print("Subtitles aren't in sync")
        return False
    return True


def has_enough_dashes(subs):
    """
    A common convention in movie subtitles, is that when the speech of 2 characters is covered by one subtitle, it is
    denoted by a dash. Some subtitles on the web do not have these dashes, which may compromise the integrity of our
    produced data, thus we must disqualify those dash-lacking subtitles..
    :param sub: a list of pysrt Subtitles.
    :return: True if it has enough dashes, False otherwise.
    """
    min_dash_threshold = 1
    dashes = 0
    for sub in subs:
        lines = re.split(r'[\n\r]', sub.text)
        for line in lines:
            if line[0] == '-':
                dashes += 1

    return dashes >= min_dash_threshold


def get_sync_measure(subs, dbs):
    """
    Checks if the subtitles match the audio.
    :param subs: a list of pysrt Subtitles.
    :param dbs: an array of the audio's dB levels.
    :return: False if not in sync OR 'subtitles' file doesn't exist.
    """
    # count how many subtitle starting times match actual peaks in the audio.
    dbs_without_infs = [dB for dB in dbs if not isinf(dB)]
    m, s = mean(dbs_without_infs), std(dbs_without_infs)
    peaks = 0
    silences = 0
    for sub in subs:
        if is_a_peak((sub.start.ordinal / 1000), dbs, m, s):
            peaks += 1
        if is_a_silence((sub.end.ordinal / 1000), dbs, m, s):
            silences += 1

    sync_measure = 0.6*(peaks / len(subs)) + 0.4*(silences / len(subs))
    print("subtitle/audio sync measure is: %.4f" % sync_measure)
    return sync_measure


def get_audio_dbs(audio_file):
    """
    :param audio_file: The path to the episode's audio file.
    :return: an array of calculated dB measurements for the audio file.
    """
    samples_per_second, wavdata = read(audio_file, mmap=True)

    # split audio to chunks to measure Db
    numchunks = int((len(wavdata) / samples_per_second) * db_measurement_chunks_per_second)
    chunks = array_split(wavdata, numchunks)
    chunks = [array(chunk, dtype='float64') for chunk in chunks]      # to prevent integer overflow
    dbs = [20*log10wrapper( mean(sqrt((chunk / 32767)**2)) ) for chunk in chunks]     # list of dB values for the chunks

    return dbs


def is_a_peak(sub_time, dbs, m, s):
    """
    :param sub_time: in seconds
    :param dbs: list of dB levels
    :param m: mean
    :param s: standard deviation
    :return: True if it's a peak, False otherwise.
    """
    silence_threshold = m - s
    talking_threshold = m + s
    chunk_i = int(sub_time * db_measurement_chunks_per_second)

    # TODO remove this block
    minutes, seconds = int(sub_time / 60), sub_time % 60
    # print("%02d,%.2f:" % (minutes, seconds), end=' ')

    silence, possible_speech, peak = False, False, False
    for i in range(-2, 6):
        # print('%.2f' % dbs[chunk_i + i], end=' ')
        if dbs[chunk_i + i] < silence_threshold:
            silence = True
            possible_speech = False
            peak = False
        elif dbs[chunk_i + i] >= talking_threshold and silence == True:
            silence = False
            peak = False
            possible_speech = True
        if dbs[chunk_i + i] > silence_threshold and possible_speech:
            peak = True
    # print("")
    return peak


def is_a_silence(sub_time, dbs, m, s):
    chunk_i = int(sub_time * db_measurement_chunks_per_second)
    interval = int(db_measurement_chunks_per_second*0.2)
    silence_threshold = m - s
    if mean(dbs[chunk_i-int(interval/2):chunk_i+interval]) < silence_threshold:
        return True
    else:
        return False

class SubtitlesNotInSyncException(Exception):
    pass


if __name__ == '__main__':
    # tests
    subs = pysrt.open('Seinfeld.S08E05.The.Package.srt', encoding='ansi ', error_handling='ignore')
    assert(not has_enough_dashes(subs))
    subs = pysrt.open('Seinfeld.S06E07.The.Soup.srt', encoding='ansi ', error_handling='ignore')
    assert(not has_enough_dashes(subs))
    subs = pysrt.open('Seinfeld.S04E07.The.Bubble.Boy.srt', encoding='ansi ', error_handling='ignore')
    assert(has_enough_dashes(subs))
