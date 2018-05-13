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

Subtitle = namedtuple('Subtitle', ["txt", "start", "end"])   # text-dialog, start-in seconds, end-in seconds

def run(screenplay_path, srt_path, laugh_track_path):
    result = []

    # read and parse data
    screenplay_parsed = parse_screenplay(screenplay_path)
    subs = parse_subtitles(srt_path)
    laugh_track = parse_laugh_track(laugh_track_path)

    # align the times of laughter with subtitles
    subs_and_laughtimes = subs + laugh_track
    subs_and_laughtimes.sort(key = lambda x: x.end if isinstance(x, Subtitle) else x)
    pass


def align_subtitles_with_screenplay(subs_and_laughtimes, screenplay):
    # TODO align dialog with screenplay
    chunk = []
    txts = []
#
#    for item in subs_and_laughtimes:
#        chunk.append(item)
#        if isinstance(item, Subtitle):
#            if '-'==item.txt[0] or '\n-' in item.txt:
#                # has at least 2 characters speaking. Split it.
#
#                we must have a match untill the dash. if not, raise eexception
#                # TODO this is a special case, need to break item!
#                txts.extend([t for t in sub.txt.split('-') if t])
#            else:
#                txts.extend([sub.txt])
#            if match_txts_against_screenplay(txts, current_dialog):
#                result.append(previous character name)
#                result.append(subs and laughes with timestamps untill that point)
#                txts = []
#                chunk = []
#                advance to next dialog line
#
    # times: subtitle start, subtitle end. LOL can be after subtitle end only.
    #
    #         match character speech: for chunk of dialog, scan subtitles untill 90% match?



    # for line in
    # 1. read .txt files to strings
    # 2. output should be screenplay only!
    # for each line in the screenplay, if it matches current line in the srt (with 90% match)
    # write it down with the starting & ending timestamp.


def parse_screenplay(screenplay_path):
    result = []
    with open(screenplay_path) as f:
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
    parser = argparse.ArgumentParser(description="Extract laughter times (in seconds) in the laugh track")
    parser.add_argument('screenplay', help='A formatted screenplay, as the one put together by screenplay_formatter.py')
    parser.add_argument('srt', help='A matching subtitles file')
    parser.add_argument('laugh_track', help='Timestamps of laughs in the laugh-track as put together by laugh_extraction.py')
    parser.add_argument('output', help="Output filename.")
    args = parser.parse_args()
    screenplay, srt, laugh_track, output = args.screenplay, args.srt, args.laugh_track, args.output

    result = run(screenplay, srt, laugh_track)

