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
from collections import namedtuple

Subtitle = namedtuple(["txt", "start", "end"])   # text-dialog, start-in seconds, end-in seconds

def run(screenplay_path, srt_path, laugh_track_path):
    screenplay_parsed = parse_screenplay(screenplay_path)
    subs = pysrt.open(srt_path)
    laugh_track = parse_laugh_track(laugh_track_path)

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
        for line in laugh_track_txt_path:
            if line[0] == '#':
                pass    # comment
            else:
                result.append(float(line.split()[0]))
    return result

def parse_subtitles(srt):
    result = []
    subs = pysrt.open(srt)
    for sub in subs:
        result.append(Subtitle(txt=sub.text,
                               start=sub.start.seconds + sub.start.minnutes*60 + sub.start.milliseconds*0.001,
                               end=sub.end.seconds + sub.end.minnutes*60 + sub.end.milliseconds*0.001))


if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Extract laughter times (in seconds) in the laugh track")
    parser.add_argument('screenplay', help='A formatted screenplay, as the one put together by screenplay_formatter.py')
    parser.add_argument('srt', help='A matching subtitles file')
    parser.add_argument('laugh_track', help='Timestamps of laughs in the laugh-track as put together by laugh_extraction.py')
    parser.add_argument('output', help="Output filename.")
    args = parser.parse_args()
    screenplay, srt, laugh_track, output = args.screenplay, args.srt, args.laugh_track, args.output

    result = run(screenplay, srt, laugh_track)

