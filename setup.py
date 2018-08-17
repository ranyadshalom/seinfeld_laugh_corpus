import setuptools

setuptools.setup(
    name='seinfeld_laugh_corpus',
    version='1.0.9',
    packages=['', 'corpus_creation',
              'corpus_creation.utils', 'corpus_creation.data_merger', 'corpus_creation.external_tools',
              'corpus_creation.subtitle_getter', 'corpus_creation.laugh_extraction',
              'corpus_creation.screenplay_downloader', 'humor_recogniser', 'humor_recogniser.data_generation_scripts'],
    package_data={'': ['the_corpus/*']},
    url='https://github.com/ranyadshalom/seinfeld_laugh_corpus',
    license='MIT',
    author='Ran Yad-Shalom, Yoav Goldberg',
    author_email='ranyadshalom@gmail.com',
    description='A humor annotated corpus of Seinfeld episodes.'
)

