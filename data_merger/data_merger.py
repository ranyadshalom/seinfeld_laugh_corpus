"""
This module merges a formatted screenplay, an .srt file and a laugh track timestamps file into
one file that includes all this data.

output format:

# CHARACTER
0 (start time in seconds)
diaolog dialog dialog
3.45 (end time in seconds)
6.55 (laugh time in seconds)
**LOL** 6.55
dialog dialog dialog
[...]
"""
import argparse
import pysrt
import re
from collections import namedtuple
from collections import defaultdict
import os
import sys

# TODO: Remove .srt formatting tags (<i>, <b>, <u>, </i>, </b>, </u>

Subtitle = namedtuple('Subtitle', ["txt", "start", "end"])   # text (dialog), start (in seconds), end (in seconds)
Result = namedtuple('Result', ["k", "score"])   # an object that contains the result of the calculations from
                                                #  the dynamic programming algorithm

match = defaultdict(dict)
match[tuple()] = defaultdict(lambda: Result(k=0, score=0))


def run(screenplay_path, srt_path, laugh_track_path, output_path):
    aligned_subs = merge(screenplay_path, srt_path)
    laugh_times = parse_laugh_track(laugh_track_path)

    write_to_file(aligned_subs, laugh_times, output_path)


def write_to_file(aligned_subs, laugh_times, output):
    with open(output, 'w') as f:
        for i, line in enumerate(aligned_subs):
            if isinstance(line, Subtitle):
                f.write("%.3f\n" % line.start)
                f.write("%s\n" % (line.txt))
                f.write("%.3f\n" % line.end)
                k = 1
                try:
                    while not isinstance(aligned_subs[i + k], Subtitle):
                        k += 1
                    next_sub_start_time = aligned_subs[i + k].start
                except IndexError:
                    next_sub_start_time = sys.float_info.max

                while laugh_times and line.start+0.5 <= laugh_times[0] <= next_sub_start_time+0.5:
                    # +0.5 because it takes the audience a moment to understand the joke
                    f.write("%.3f\n" % laugh_times[0])
                    f.write("**LOL**\n")
                    laugh_times = laugh_times[1:]
            else:
                # character name
                f.write("# %s" % line[1])


def merge(screenplay_path, srt_path):
    """

    :param screenplay_path: path to a Seinfeld screenplay, in a READABLE format (generated by screenplay_formatter.py).
    :param srt_path: path to a matching .srt subtitle file (make sure the timing is correct).
    :return:
    """
    # read and parse data
    screenplay_parsed = parse_screenplay(screenplay_path)
    screenplay_parsed = remove_characters_without_dialog(screenplay_parsed)
    subs = parse_subtitles(srt_path)
    # process data
    dialog_lines = [line[1] for line in screenplay_parsed if line[0]=='dialog']
    delimiters = get_optimal_match(dialog_lines, subs)
    aligned_subs = align_subtitles_with_screenplay(subs, screenplay_parsed, delimiters)

    return aligned_subs


def parse_screenplay(screenplay_path):
    """
    :param screenplay_path: A properly formatted Seinfeld screenplay (use screenplay_formatter.py).
    :return: The screenplay as a list of tuples of the form
             [('character_name', 'JERRY'), ('dialog', 'bla bla bla'), ...]
    """
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
    subs = pysrt.open(srt, encoding='ansi ')
    for sub in subs:
        start, end = get_sub_time_in_seconds(sub.start), get_sub_time_in_seconds(sub.end)
        if '-'==sub.text[0] or '\n-' in sub.text:
            # if more than one character is speaking, split subtitle
            splitted = [s for s in re.split('(?:^-)|(?:\n-)',sub.text) if s]
            try:
                sub_a, sub_b = splitted
            except ValueError:
                print("ERROR! Problematic subtitle: '%s'. \nPlease remove unnecessary dashes from it and try again.\n" % sub.text)
                quit()
            between_time = start/2 + end/2
            result.append(Subtitle(txt=sub_a, start= start, end=between_time))
            result.append(Subtitle(txt=sub_b, start=between_time, end=end))
        else:
            result.append(Subtitle(txt=sub.text, start=start, end=end))
    return result


def get_sub_time_in_seconds(sub_time):
    return sub_time.seconds + sub_time.minutes*60 + sub_time.milliseconds*0.001


def get_optimal_match(dialog_lines, subtitles):
    """
    A dynamic programming algorithm that returns the optimal screenplay/subtitles match.
    :param dialog_lines: A list of strings. Contains all the dialog lines being said. A dialog line here is NOT defined
                         as a line per se but as all the character has to say before being interrupted by another
                         character / a scene transition / the end.
    :param subtitles: A list of Subtitle objects, as defined by the 'pysrt' package:
                      https://github.com/byroot/pysrt
    :return: A list of delimiters (integers) that indicate the optimal match between the dialog and the subtitles.
             Those integers indicate where exactly to cut the subtitle list in order to get chunks that exactly match
             the dialog list.
    """
    D = tuple(dialog_lines)
    S = tuple(subtitles)

    # calculate dynamic programming table
    for i in range(1, len(D) + 1):
        for j in range(len(S)):
            match[ D[-i:] ][ S[j:] ] = get_max_k(D[-i:], S[j:])

    # backtrack solution
    delimiters = [0]
    k = 0
    while D:
        k = match[D][S].k
        delimiters.append(k + delimiters[-1])
        D = D[1:]
        S = S[k:]
    return delimiters


def get_max_k(D, S):
    """
    finds a k that maximizes the score of the match
    :param D: A tuple of dialog lines.
    :param S: A tuple of subtitles.
    :return: The k (the partition point) which maximizes the matching score.
    """
    # A limit for the amount of subtitles that can fit a line of dialog.
    # (Without a reasonable pruning window, calculation becomes too slow.)
    WINDOW = 14

    max_score = 0
    max_k = None

    for k in range(min(WINDOW, len(S))):
        s = get_score(D[0], S[:k]) + match[ D[1:] ][ S[k:] ].score
        if s > max_score:
            max_score = s
            max_k = k

    return Result(k=max_k, score=max_score)


def get_score(dialog, subs):
    """
    :param subs: A list containing the substitles we try to match to this dialog line.
    :param dialog:  A dialog line (i.e. a character's dialog block from the screenplay).
    :return: the matching's score.
    """
    # will run untill match cannot improve anymore
    txt_from_subtitles = "\n".join(sub.txt for sub in subs)

    txt_from_subtitles = re.sub(r'\\','',txt_from_subtitles) # remove escape characters from subtitles.
    txt_from_dialog = re.sub(r'[\`\’]', '\'', dialog) # allow only ' character as a dash

    # remove punctuation
    words_from_subtitles = set(re.split(r'[\s\,\.\?\!\;\:"]', txt_from_subtitles.lower()))
    words_from_dialog = set(re.split(r'[\s\,\.\?\!\;\:"]', txt_from_dialog.lower()))

    # calculate BOW intersection and union
    intersection = len(words_from_dialog & words_from_subtitles)
    union = len(words_from_dialog | words_from_subtitles)

    return intersection / union


def align_subtitles_with_screenplay(subs, screenplay, delimiters):
    result = []

    for i,j in zip(delimiters, delimiters[1:]):
        result.append(screenplay[0])
        screenplay = screenplay[2:]
        result.extend(subs[i:j])

    return result


def remove_characters_without_dialog(screenplay):
    """
    remove double 'character' instances from screenplay (happens when a character
    does something, but doesn't actually speak, e.g. GEORGE: (gasps)
    """
    redundant_indices_in_screenplay = []
    for i in range(len(screenplay)-1):
        if screenplay[i][0] == 'character_name' and screenplay[i+1][0] == 'character_name':
            redundant_indices_in_screenplay.append(i)

    redundant_indices_in_screenplay.reverse()
    for i in redundant_indices_in_screenplay:
        del screenplay[i]

    return screenplay


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Merge 3 types of data (subtitles, laughter cues & screenplay) into one coherent file.")
    parser.add_argument('screenplay', help='A formatted screenplay, as the one put together by screenplay_formatter.py')
    parser.add_argument('srt', help='A matching subtitles file')
    parser.add_argument('laugh_track', help='Timestamps of laughs in the laugh-track as put together by laugh_extraction.py')
    parser.add_argument('output', help="Output filename.")
    args = parser.parse_args()
    screenplay, srt, laugh_track, output = args.screenplay, args.srt, args.laugh_track, args.output

    if os.path.exists(output):
        print("'%s' already exists!\n" % output)
    else:
        result = run(screenplay, srt, laugh_track, output)
