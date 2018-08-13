from collections import Counter
from collections import defaultdict
import csv
import re
from functools import reduce

from humor_recogniser.screenplay import Screenplay
from humor_recogniser.ml_humor_recogniser import read_data
from humor_recogniser.screenplay import Laugh, Line

screenplays = read_data('../the_corpus/')
episodes_results = {}


def find_prev_character(screenplay, i):
    k = 0
    while True:
        if i - k < 0:
            print("Too early, no prev character")
        k += 1
        if isinstance(screenplay[i - k], Line):
            if screenplay[i].character != screenplay[i - k].character:
                return screenplay[i-k].character

# Count number of laughs for character per episode.
for screenplay in screenplays:
    print("For filename: %s" % screenplay.filename)
    laugh_counter = Counter()
    line_counter = Counter()
    for i, line in enumerate(screenplay):
        if isinstance(line, Laugh):
            if isinstance(screenplay[i-1], Line):
                k = 1
                prev_character = find_prev_character(screenplay, i-1)
                if prev_character:
                    laugh_counter[prev_character] += 1
        elif isinstance(line, Line):
            # add count prev character
            prev_character = find_prev_character(screenplay, i)
            if prev_character:
                line_counter[prev_character] += 1

    sorted_list = list(laugh_counter.items())
    sorted_list.sort(key=lambda t: t[1], reverse=True)
    for i, name_count in enumerate(sorted_list):
        name, count = name_count
        print("%d. %s: %d laughs." % (i+1, name, count))
    episodes_results[screenplay.filename] = sorted_list
    print("\n")

    merged_sorted_list = [(character, line_counter[character], laugh_counter[character]) for character in line_counter.keys()]
    merged_sorted_list.sort(key=lambda t: t[1], reverse=True)
    for i, name_count_count in enumerate(merged_sorted_list):
        name, line_count, laugh_count = name_count_count
        print("%d. %s: %d lines, %d laughs. Funniness: %.3f" % (i+1, name, line_count, laugh_count, laugh_count / line_count))
    episodes_results[screenplay.filename] = merged_sorted_list
    print("\n")
################################################################


# print funniness
all_counts = reduce(lambda x, y: x + y, episodes_results.values())


def sum_up_character_lines_and_laughs(character):
    lines = sum(c[1] for c in all_counts if c[0] == character)
    laughs = sum(c[2] for c in all_counts if c[0] == character)
    return character, lines, laughs


characters = set((character for character, _, _ in all_counts))
aggregated_counts = map(sum_up_character_lines_and_laughs, characters)
print("Total lines/laughs/funniness measures:")
for character, lines, laughs in aggregated_counts:
    if lines > 400:
        print("%s,%d,%d,%.3f" % (character, lines, laughs, laughs/lines))
#############################################################################

# cluster episodes indirect laughter
# TODO

############################################################################



# count laugh distribution across the average episode
laugh_dist = Counter()
time_unit = 60  # in seconds
for screenplay in screenplays:
    for line in screenplay:
        if isinstance(line, Laugh):
            laugh_dist[int(line.time / time_unit)] += 1
laugh_dist = [(time, num_laughs) for time, num_laughs in laugh_dist.items()]
laugh_dist.sort(key=lambda x: x[0])

print("Distribution of laughter in the average episode, by minutes")
print(",".join(str(l[1]) for l in laugh_dist))
#############################################################################


# count laughs across seasons
laughs_per_season = Counter()
for screenplay in screenplays:
    m = re.findall(r'\d+', screenplay.filename)
    se, ep = int(m[0]), int(m[1])
    for line in screenplay:
        if isinstance(line, Laugh):
            laughs_per_season[se] += 1
print("Laughs per season:")
print(laughs_per_season)
##############################################################################

# total laughs per episode
laughs_per_episode = Counter()
for i, screenplay in enumerate(screenplays):
    for line in screenplay:
        if isinstance(line, Laugh):
            laughs_per_episode[i] += 1
print("Laughs per episode:")
print(",".join(str(num_laughs) for num_laughs in laughs_per_episode.values()))
################################################################################

with open('stats_indirect.csv', 'w') as csvfile:
    fieldnames = ['character'] + [s.filename for s in screenplays]
    csvwriter = csv.DictWriter(csvfile, fieldnames)
    dict_for_csv = defaultdict(dict)

    csvwriter.writeheader()
    for episode, results in episodes_results.items():
        for name, _, count in results:
            dict_for_csv[name][episode] = count

    for name in dict_for_csv.keys():
        csvwriter.writerow({'character': name, **dict_for_csv[name]})

