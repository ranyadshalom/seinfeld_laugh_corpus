from collections import Counter
from collections import defaultdict
import csv

from humor_recogniser.screenplay import Screenplay
from humor_recogniser.ml_humor_recogniser import read_data
from humor_recogniser.screenplay import Laugh, Line

screenplays = read_data(__file__.rsplit('/', 1)[0])
episodes_results = {}

# Count number of laughs for character per episode.
for screenplay in screenplays:
    print("For filename: %s" % screenplay.filename)
    counter = Counter()
    for i, line in enumerate(screenplay):
        if isinstance(line, Laugh):
            if isinstance(screenplay[i-1], Line):
                counter[screenplay[i-1].character] += 1
    sorted_list = list(counter.items())
    sorted_list.sort(key=lambda t: t[1], reverse=True)
    for i, name_count in enumerate(sorted_list):
        name, count = name_count
        print("%d. %s: %d laughs." % (i+1, name, count))
    episodes_results[screenplay.filename] = sorted_list
    print("\n")

with open('stats.csv', 'w') as csvfile:
    fieldnames = ['character'] + [s.filename for s in screenplays]
    csvwriter = csv.DictWriter(csvfile, fieldnames)
    dict_for_csv = defaultdict(dict)

    csvwriter.writeheader()
    for episode, results in episodes_results.items():
        for name, count in results:
            dict_for_csv[name][episode] = count

    for name in dict_for_csv.keys():
        csvwriter.writerow({'character': name, **dict_for_csv[name]})

