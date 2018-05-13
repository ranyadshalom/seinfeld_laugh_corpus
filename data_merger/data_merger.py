"""
This module merges a formatted screenplay, an .srt file and a laugh track timestamps file into
one file that includes all this data.

output format:

# CHARACTER
00:00:00:00 (start timecode)
diaolog dialog dialog
00:00:00:00 (end timecode)
LOL
00:00:00:00 (start timecode)
dialog dialog dialog
# CHARACTER
dialog dialog
00:00:00:00 (end timecode
LOL

"""
import argparse
import pysrt
import re
from collections import namedtuple

Subtitle = namedtuple('Subtitle', ["txt", "start", "end"])   # text (dialog), start (in seconds), end (in seconds)

def run(screenplay_path, srt_path, laugh_track_path):
    result = []

    # read and parse data
    screenplay_parsed = parse_screenplay(screenplay_path)
    subs = parse_subtitles(srt_path)
    laugh_track = parse_laugh_track(laugh_track_path)

    # align the times of laughter with subtitles
    subs_and_laughtimes = subs + laugh_track
    subs_and_laughtimes.sort(key = lambda x: x.end if isinstance(x, Subtitle) else x)

    result = align_subtitles_with_screenplay(subs_and_laughtimes, screenplay_parsed)
    print([line for line in result]) # TODO remove this. for testing purposes


def align_subtitles_with_screenplay(subs_and_laughtimes, screenplay):
    result = []
    chunk = []
    txt = ""
    screenplay_lines = iter(screenplay)
    result.append(next(screenplay_lines))
    next_line = next(screenplay_lines)

    for item in subs_and_laughtimes:
        chunk.append(item)
        if isinstance(item, Subtitle):
            txt += item.txt + '\n'
            if match_txts_against_screenplay(txt, next_line[1]):
                print("MATCH! \n%s\n%s" % (txt, next_line[1]))
                result.extend(chunk)
                result.append(next(screenplay_lines)) # next character name
                next_line = next(screenplay_lines)
                if next_line[0] != 'dialog':
                    raise ValueError("screenplay file violates character/dialog order!")
                txt = ""
                chunk = []

    return result


def match_txts_against_screenplay(txt_from_subtitles, txt_from_dialog):
    """
    # TODO the right way is to find the maximum match for each line of dialog!
    # TODO usually when the 'intersection' variable freezes, it means that the maximum match has been reached.
    """
    txt_from_subtitles = re.sub(r'\\','',txt_from_subtitles) # remove escape characters from subtitles.
    txt_from_dialog = re.sub(r'[\`\’]', '\'', txt_from_dialog) # allow only ' character as a dash

    # remove punctuation
    words_from_subtitles = set(re.split(r'[\s\,\.\?\!\;\:]', txt_from_subtitles.lower()))
    words_from_dialog = set(re.split(r'[\s\,\.\?\!\;\:]', txt_from_dialog.lower()))

    # calculate BOW intersection and union
    intersection = len(words_from_dialog & words_from_subtitles)
    union = len(words_from_dialog | words_from_subtitles)

    return (intersection / union) >= 0.8


def parse_screenplay(screenplay_path):
    result = []
    with open(screenplay_path, encoding='utf8') as f:
        for line in f:
            if line[0] == '#' or line=='\n':
                pass    # a comment, a new line...
            elif line.isupper():
                result.append(['character_name', line]) # a character's name
            else:
                if result[-1][0] == 'dialog':
                    result[-1][1] += line
                else:
                    result.append(['dialog', line])
    return result


def parse_laugh_track(laugh_track_txt_path):
    result = []
    with open(laugh_track_txt_path) as f:
        for line in f:
            if line[0] == '#':
                pass    # comment
            else:
                result.append(float(line.split()[0]))
    return result


def parse_subtitles(srt):
    result = []
    subs = pysrt.open(srt)
    for sub in subs:
        start, end = get_sub_time_in_seconds(sub.start), get_sub_time_in_seconds(sub.end)
        if '-'==sub.text[0] or '\n-' in sub.text:
            # if more than one character is speaking, split subtitle
            splitted = [s for s in re.split('(?:^-)|(?:\n-)',sub.text) if s]
            sub_a, sub_b = splitted
            between_time = start/2 + end/2
            result.append(Subtitle(txt=sub_a, start= start, end=between_time))
            result.append(Subtitle(txt=sub_b, start=between_time, end=end))
        else:
            result.append(Subtitle(txt=sub.text, start=start, end=end))
    return result

def get_sub_time_in_seconds(sub_time):
    return sub_time.seconds + sub_time.minutes*60 + sub_time.milliseconds*0.001

if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Merge 3 types of data (subtitles, laughter cues & screenplay) into one coherent file.")
    parser.add_argument('screenplay', help='A formatted screenplay, as the one put together by screenplay_formatter.py')
    parser.add_argument('srt', help='A matching subtitles file')
    parser.add_argument('laugh_track', help='Timestamps of laughs in the laugh-track as put together by laugh_extraction.py')
    parser.add_argument('output', help="Output filename.")
    args = parser.parse_args()
    screenplay, srt, laugh_track, output = args.screenplay, args.srt, args.laugh_track, args.output

    result = run(screenplay, srt, laugh_track)

