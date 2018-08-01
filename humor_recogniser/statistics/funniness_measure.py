from collections import Counter
from collections import defaultdict
import csv


from humor_recogniser.screenplay import Screenplay
from humor_recogniser.ml_humor_recogniser import read_data
from humor_recogniser.screenplay import Laugh, Line

screenplays = read_data('../../the_corpus/')
episodes_results = {}

# Count number of laughs and lines for character per episode.
for screenplay in screenplays:
    print("For filename: %s" % screenplay.filename)
    laugh_counter = Counter()
    line_counter = Counter()
    for i, line in enumerate(screenplay):
        if isinstance(line, Laugh):
            if isinstance(screenplay[i-1], Line):
                laugh_counter[screenplay[i - 1].character] += 1
        elif isinstance(line, Line):
                line_counter[line.character] += 1
    merged_sorted_list = [(character, line_counter[character], laugh_counter[character]) for character in line_counter.keys()]
    merged_sorted_list.sort(key=lambda t: t[1], reverse=True)
    for i, name_count_count in enumerate(merged_sorted_list):
        name, line_count, laugh_count = name_count_count
        print("%d. %s: %d lines, %d laughs. Funniness: %.3f" % (i+1, name, line_count, laugh_count, laugh_count / line_count))
    episodes_results[screenplay.filename] = merged_sorted_list
    print("\n")

with open('funniness_measures.csv', 'w') as csvfile:
    fieldnames = ['character'] + [s.filename for s in screenplays]
    csvwriter = csv.DictWriter(csvfile, fieldnames)
    dict_for_csv = defaultdict(dict)

    csvwriter.writeheader()
    for episode, results in episodes_results.items():
        for name, line_count, laugh_count in results:
            dict_for_csv[name+'_lines'][episode] = line_count
            dict_for_csv[name+'_laughs'][episode] = laugh_count
            dict_for_csv[name+'_funniness'][episode] = laugh_count / line_count

    for name in dict_for_csv.keys():
        csvwriter.writerow({'character': name, **dict_for_csv[name]})

