from collections import Counter
from collections import defaultdict
import re
from functools import reduce
import csv
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from numpy import mean
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import matplotlib_venn as venn

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
###########################################################################


# cluster funniness vectors for each episode
def get_funniness_vector(args):
    episode_name, characters_laughs = args
    characters_laughs = {c[0]: c[2] / c[1] for c in characters_laughs}
    v = []
    for character in ["JERRY", "GEORGE", "ELAINE", "KRAMER"]:
        v.append(characters_laughs[character])

    v= np.array(v)
    norm = np.linalg.norm(v, ord=1)
    return (v / norm, episode_name[:-7])

vectors_and_episode_names = list(map(get_funniness_vector, episodes_results.items()))
X = np.array([x for x, _ in vectors_and_episode_names])
episode_names = [y for _, y in vectors_and_episode_names]

kmeans = KMeans(n_clusters=4, random_state=0).fit(X)
print("EPISODE CLUSTERING BY CHARACTER FUNNINESS VECTORS")
for vector_name, label in zip(vectors_and_episode_names, kmeans.labels_):
    vector, name = vector_name
    print("%s,%d,,%.4f,%.4f,%.4f,%.4f" % (name, label, vector[0], vector[1], vector[2],vector[3]))


##########################################################################
# find trigger words
lmtz = WordNetLemmatizer()


def find_trigger_words(all_lines_txt, funny_lines_txt, limit=30, normalization=True):
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
    for word, funniness in word_funniness_sorted[:limit]:
        print("%s,%.3f" % (word, funniness))
    return word_funniness_sorted[:limit]


all_lines_txt = [line.txt for line in all_lines]
funny_lines_txt = [line.txt for line in funny_lines]
trigger_words = find_trigger_words(all_lines_txt, funny_lines_txt, limit=33)
############################################################################
# Analyze trigger words using LIWC word groups
def load_liwc():
    result = {}
    with open("LIWC_Features.txt") as f:
        for line in f:
            try:
                category, words = line.split(",", maxsplit=1)
                words = [w.strip() for w in words.split(",")]
                result[category] = words
            except ValueError:
                print("LIWC: Skipping line '%s'" % line)
        return result

liwc = load_liwc()
trigger_words_categories = defaultdict(set)

for trigger_word, _ in trigger_words:
# for word in trigger_words:
    for category, words in liwc.items():
        for liwc_word in words:
            if liwc_word.endswith("*"):
                regex = "%s.*" % liwc_word[:-1]
            else:
                regex = liwc_word
            if re.match(regex, trigger_word):
                trigger_words_categories[category].add(trigger_word)

trigger_words_categories_sorted = [(category, words) for category, words in trigger_words_categories.items()]
trigger_words_categories_sorted.sort(key=lambda x: len(x[1]), reverse=True)
for category, words in trigger_words_categories_sorted:
    print("%s: %s" % (category, words))

# plot venn diagrams
sets = [s for _, s in trigger_words_categories_sorted[:3]]
labels = tuple([l for l, _ in trigger_words_categories_sorted[:3]])
venn.venn3(sets, set_labels=labels)
plt.show()

############################################################################

# trigger words per episode:
per_episode = []
for screenplay in screenplays:
    local_funny_lines = []
    local_lines = []
    print("Trigger words in '%s':" % screenplay.filename)
    for i, line in enumerate(screenplay):
        if isinstance(line, Laugh):
            if isinstance(screenplay[i-1], Line):
                local_funny_lines.append(screenplay[i-1])
    episode_funny_text = [line.txt for line in local_funny_lines]
    per_episode.append((screenplay.filename,
                       find_trigger_words(funny_lines_txt, episode_funny_text, limit=3)))

for episode_name, trigger_words in per_episode:
    if any(y > 0.7 for _,y in trigger_words):
        formatted = episode_name[9:-7].replace("."," ")
        print("%s,%s,%.3f" % (formatted, trigger_words[0][0], trigger_words[0][1]))

#################################################################


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
############################################################################



