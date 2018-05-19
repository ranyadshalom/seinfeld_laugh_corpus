"""
This module merges a formatted screenplay, an .srt file and a laugh track timestamps file into
one file that includes all this data.

output format:

# CHARACTER
0 (start time in seconds)
diaolog dialog dialog
3.45 (end)
**LOL**
6.55
dialog dialog dialog
[...]
"""
import argparse
import pysrt
import re
from collections import namedtuple
from collections import defaultdict
from timeit import default_timer as timer

# TODO: Character name should be closer to when a character starts speaking, not when a previous character finishes speaking.
# TODO: Remove .srt formatting tags (<i>, <b>, <u>, </i>, </b>, </u>
# TODO: Dynamic programming

Subtitle = namedtuple('Subtitle', ["txt", "start", "end"])   # text (dialog), start (in seconds), end (in seconds)
Result = namedtuple('Result', ["k", "score"])   # an object that contains the result of the calculations in the dynamic programming algorithm

match = defaultdict(dict)
match[tuple()] = defaultdict(lambda: Result(k=0,score=0))


def measure_execution_time(foo):
    def wrapper(*args, **kwargs):
        start = timer()
        result = foo(*args, **kwargs)
        end = timer()
        if end - start > 2:
            print ("%s took %.2f seconds to execute!" % (foo.__name__, end-start))
        return result
    return wrapper


def run(screenplay_path, srt_path, laugh_track_path, output_path):
    result = merge(screenplay_path, srt_path, laugh_track_path)

    write_to_file(result, output)


def write_to_file(result, output):
    with open(output, 'w') as f:
        for line in result:
            if isinstance(line, Subtitle):
                # f.write("%f\n%s\n%f\n" % (line.start, line.txt, line.end))
                f.write("%s\n" % (line.txt))
            elif isinstance(line, float):
                f.write("**LOL**\n")
            else:
                # character name
                f.write("# %s" % line[1])


def merge(screenplay_path, srt_path, laugh_track_path):
    # read and parse data
    screenplay_parsed = parse_screenplay(screenplay_path)
    subs = parse_subtitles(srt_path)
    laugh_track = parse_laugh_track(laugh_track_path)

    # process data
    dialog_lines = [line[1] for line in screenplay_parsed if line[0]=='dialog']
    delimiters = get_optimal_match(dialog_lines, subs)

    # aligned_subs = align_subtitles_with_screenplay(subs, screenplay_parsed)
    # align the times of laughter with subtitles
    final_result = aligned_subs + laugh_track
    final_result.sort(key = sort_key)

    return final_result


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


def sort_key(item):
    if isinstance(item, Subtitle):
        return item.end
    elif isinstance(item, float):
        return item
    else:
        # dialog. return its timestamp which is supposed to be its last element.
        return item[-1]


def get_optimal_match(dialog_lines, subtitles):
    """
    A dynamic programming algorithm that returns the optimal screenplay/subtitles match.
    :param screenplay:
    :param subtitles:
    :return:
    """
    D = tuple(dialog_lines)
    S = tuple(subtitles)

    # calculate
    for i in range(1, len(D) + 1):
        for j in range(len(S)):
            match[ D[-i:] ][ S[j:] ] = get_max_k(D[-i:], S[j:])

    # get value
    delimiters = []
    while D:
        k = match[D][S].k
        delimiters.append(k)
        D = D[1:]
        S = S[k:]
    return delimiters


@measure_execution_time
def get_max_k(D, S):
    """
    finds a k that maximizes the score of the match
    :param D:
    :param S:
    :return:
    """
    max_score = 0
    max_k = None

    for k in range(len(S)):
        s = get_score(D[0], S[:k]) + match[ D[1:] ][ S[k:] ].score
        if s > max_score:
            max_score = s
            max_k = k

    return Result(k=max_k, score=max_score)


@measure_execution_time
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



if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Merge 3 types of data (subtitles, laughter cues & screenplay) into one coherent file.")
    parser.add_argument('screenplay', help='A formatted screenplay, as the one put together by screenplay_formatter.py')
    parser.add_argument('srt', help='A matching subtitles file')
    parser.add_argument('laugh_track', help='Timestamps of laughs in the laugh-track as put together by laugh_extraction.py')
    parser.add_argument('output', help="Output filename.")
    args = parser.parse_args()
    screenplay, srt, laugh_track, output = args.screenplay, args.srt, args.laugh_track, args.output

    result = run(screenplay, srt, laugh_track, output)

