Seinfeld Laugh Corpus
=====================

Seinfeld Laugh Corpus is a humor annotated corpus of 96 Seinfeld episodes
from seasons 4-9. You can read about the methods we used to generate it along with some interesting statistics in the project's `paper`_.

The raw corpus can be found in the `corpus`_ directory of this repository.


Installation
~~~~~~~~~~~~

On Python 3:

.. code:: sh

   $ pip3 install seinfeld_laugh_corpus

Quick Start
~~~~~~~~~~~

.. code:: python

   >>> from seinfeld_laugh_corpus import corpus
   >>> seinfeld = corpus.load()

   >>> # first index is the episode number, second index is the line number.
   >>> print(seinfeld[1][0])
   Line(character='JERRY', txt='Have you ever called someone and were  disappointed when they answered?', start=0.62, end=5.011)
   >>> print(seinfeld[1][1])
   Laugh(time=2.3)


Getting a specific episode:

.. code:: python

   >>> seinfeld.search("marine biologist")
   Screenplay('S05E14 The Marine Biologist')
   >>> seinfeld[(5,14)]
   Screenplay('S05E14 The Marine Biologist')

You can also load the corpus with the laughs folded into the lines. In that case, if a line is followed by a laugh, its "is_funny" attribute will be set to True.

.. code:: python

   >>> seinfeld = corpus.load(fold_laughs=True)
   >>> print(seinfeld[1][0])
   Line(character='JERRY', txt='Have you ever called someone and were  disappointed when they answered?', start=0.62, end=5.011, is_funny=True, laugh_time=2.3)


----


From the corpus:

::

  # DONALD
  975.851
  What are you looking at?
  977.179
  977.252
  Never seen a kid in a bubble before?
  979.946
  980.400
  **LOL**
  # GEORGE
  983.158
  Of course I have. Come on.
  985.886
  985.961
  My cousin's in a bubble.
  988.859
  988.300
  **LOL**
  989.664
  My friend Jeffrey's sister also,
  bubble, you know...
  993.256
  993.200
  **LOL**
  993.402
  I got a lot of bubble experience.
  Come on.
  996.062
  # DONALD
  996.805
  What's your story?
  998.738
  # SUSAN
  998.738
  I have no story.
  1000.671
  # GEORGE
  1000.742
  She works for NBC.
  1002.969
  # DONALD
  1003.045
  How about taking your top off?
  1005.511
  1005.300
  **LOL**


More Information
~~~~~~~~~~~~~~~~

-  The project’s `paper`_.
-  The code we used to generate the corpus is in the 'corpus_creation' directory. You are free to use it if you'd like to generate your own humor annotated corpus using our method, although you will need to make modifications in order to adjust it to your specific case.
-  Also, make sure that both ffmpeg and sox portable versions in the
   ‘external_tools’ folder. We have chosen not to include them in this repository.


.. _paper: https://github.com/ranyadshalom/the_seinfeld_corpus/raw/master/paper.pdf
.. _corpus: https://github.com/ranyadshalom/seinfeld_laugh_corpus/tree/master/seinfeld_laugh_corpus/the_corpus