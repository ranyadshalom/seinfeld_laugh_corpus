# THIS SECTION CAN BE IGNORED FOR THE WHILE AS IT MAINLY CONSISTS OF NOTES TO SELF, THOUGHTS AND PONDERING.
# WRITING IT ALL DOWN HELPS ME MAKE DECISIONS AND REACH CONCLUSIONS.

# Before implementation, I'd like to try and plan as much as possible in advance, so that I will not have to
# realize half way through that what I've done will make it impossible to extract feature X or to give result Y.


# Text-based feature idea list:
#
#   * The character that speaks
#   * The character that last spoke
#   * How many sentences ago the last character spoke / how many subtitles ago the last character spoke
#   * The last sentence (simplified - sentiment score, semantic value [based on word2vec])
#   * This sentence (simplified)
#   * Language model (try a bunch of them, and even generate one if needs) value of this sentence.
#   *

# Time-based feature idea list:
# NOTE TO SELF: THESE FEATURES ARE NOT BINARY! You've never worked with such features before. Please make sure you're
#               doing it right, lest they will be utterly meaningless (no joke has the exact same timing data).
#
#   * How long it took to say this sentence considering the number of syllables (longer-lingering sentences maye funnier?)
#   * How much SILENCE do we have before the joke? (this might be a good indicator, but it is not always available).
#   *

# Possible problems and solutions:
#   Q: How to deal with a sentence that's spread across 2 subtitles and more?
#   A: Don't need to. It almost never happens (can count exactly how many times in all my data to demonstrate this point)

#   Q: Not all sentences / dialog lines have timestamps, since sometimes 2 characters' sentences are spread across
#      one subtitle. How should I deal with that?
#   A: It's just gonna be left out of the feature vector... it's OK...



# 1. Read data file into memory
#       Q: How best should I store the data in the memory?
#       A: Same as it is in the file, just provide a good and intuitive interface to it.
# 2. Split: 80% train, 20% test.
# 3. Train model (for each subtitle: a vector of features / produces laughter or not)
# 4. Test on the test set.
import os
from humor_recogniser.screenplay import Screenplay

data = []


def read_data(data_folder):
    files = (f for f in os.listdir(data_folder) if os.path.isfile(data_folder + '/' + f))
    for file in files:
        try:
            screenplay = Screenplay.from_file(file)
            data.append(screenplay)
        except:
            print("ERROR reading data file '%s'. Skipped." % file)

# How should the data be represented in the memory?
# A laugh could only appear in the data after a subtitle. Thus the decision has to be made
# after each subtitle.
#