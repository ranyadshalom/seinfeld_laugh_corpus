from collections import Counter
from collections import defaultdict
from functools import reduce
import csv
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from numpy import mean


from humor_recogniser.screenplay import Screenplay
from humor_recogniser.ml_humor_recogniser import read_data
from humor_recogniser.screenplay import Laugh, Line


screenplays = read_data('../../the_corpus/')
episodes_results = {}
all_lines = []
funny_lines = []

# Count number of laughs and lines for character per episode.
for screenplay in screenplays:
    print("For filename: %s" % screenplay.filename)
    laugh_counter = Counter()
    line_counter = Counter()
    for i, line in enumerate(screenplay):
        if isinstance(line, Laugh):
            if isinstance(screenplay[i-1], Line):
                laugh_counter[screenplay[i - 1].character] += 1
                funny_lines.append(screenplay[i-1])
        elif isinstance(line, Line):
                line_counter[line.character] += 1
                all_lines.append(line)
    merged_sorted_list = [(character, line_counter[character], laugh_counter[character]) for character in line_counter.keys()]
    merged_sorted_list.sort(key=lambda t: t[1], reverse=True)
    for i, name_count_count in enumerate(merged_sorted_list):
        name, line_count, laugh_count = name_count_count
        print("%d. %s: %d lines, %d laughs. Funniness: %.3f" % (i+1, name, line_count, laugh_count, laugh_count / line_count))
    episodes_results[screenplay.filename] = merged_sorted_list
    print("\n")

# print funniness
all_counts = reduce(lambda x, y: x + y, episodes_results.values())


def sum_up_character_lines_and_laughs(character):
    lines = sum(c[1] for c in all_counts if c[0] == character)
    laughs = sum(c[2] for c in all_counts if c[0] == character)
    return character, lines, laughs


characters = set((character for character, _, _ in all_counts))
aggregated_counts = map(sum_up_character_lines_and_laughs, characters)
print("Total laughs/lines/funniness measures:")
for character, lines, laughs in aggregated_counts:
    if lines > 400:
        print("%s,%d,%d,%.3f" % (character, lines, laughs, laughs/lines))


##########################################################################
# find trigger words
lmtz = WordNetLemmatizer()


def find_trigger_words(all_lines_txt, funny_lines_txt):
    all_words = [lmtz.lemmatize(word.lower()) for word in nltk.word_tokenize("\n".join(all_lines_txt))]
    funny_words = [lmtz.lemmatize(word.lower()) for word in nltk.word_tokenize("\n".join(funny_lines_txt))]
    all_words_dist = nltk.FreqDist(all_words)
    funny_words_dist = nltk.FreqDist(funny_words)

    all_words_mean = mean(list(all_words_dist.values()))
    compute_funniness = lambda word: (funny_words_dist[word] / all_words_dist[word]) * min(all_words_dist[word]/all_words_mean, 1)
    word_funniness = {word: compute_funniness(word) for word in set(all_words)}
    word_funniness_sorted = [(word, funniness) for word, funniness in word_funniness.items()]
    word_funniness_sorted.sort(key=lambda x:x[1], reverse=True)
    print("word funniness:")
    for word, funniness in word_funniness_sorted[:30]:
        print("%s,%.3f" % (word, funniness))


all_lines_txt = [line.txt for line in all_lines]
funny_lines_txt = [line.txt for line in funny_lines]
find_trigger_words(all_lines_txt, funny_lines_txt)
############################################################################


# trigger words for each character:
characters = ["JERRY", "ELAINE", "GEORGE", "KRAMER"]
for character in characters:
    all_lines_txt = [line.txt for line in all_lines]
    funny_lines_txt = [line.txt for line in funny_lines if line.character == character]
    print("Trigger words for %s:" % character)
    find_trigger_words(all_lines_txt, funny_lines_txt)

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

