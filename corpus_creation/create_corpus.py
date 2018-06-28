"""
A module that creates the annotated Seinfeld corpus from scratch, given the episodes in .mkv format.
"""

import argparse
import os


def run(episodes_path):
    for _, dirpath, filenames in os.walk(episodes_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            process(file_path)


class Processor:
    """
    A class that generates corpus data from a Seinfeld episode in the .mkv file format.
    """
    def __init__(self, filepath, outputpath):
        self.filepath = filepath      # path of the video file of the episode
        self.outputpath = outputpath  # path of the folder in which to write the output
        self.files = {}               # paths of all the temporary files that will be used in the processing

    def process(self):
        filename = self.filepath.rsplit('/', 1)[1]
        try:
            self.files['audio'] = extract_audio_from(filepath)
            self.files['laughter_times'] = extract_laughter_times(audio_filepath)
            self.files['subtitles'] = get_subtitles(filepath, audio_filepath)
            self.files['screenplay'] = get_screenplay(filename)
            merge(self.files['screenplay'], self.files['subtitles'], self.files['laughter_times'])
        except AudienceRecordingNotInStereoException:
            print("ERROR for '%s': Audience recording is not in Stereo." % filename)
        except SubtitlesNotInSyncException:
            print("ERROR for '%s': Subtitles not in sync." % filename)
        except ScreenplayParseException:
            print("ERROR for '%s': Screenplay parsing error." % filename)
        except MergeException:
            print("ERROR for '%s': Merging error." % filename)
        except Exception as e:
            print("ERROR for '%s': %s" % (filename, str(e)))
        else:
            print("SUCCESS for '%s'." % filename)
        finally:
            print("Cleaning up...")
            self._cleanup()

    def _cleanup(self):
        for filename in self.files.items():
            os.remove(filename)
            print("Removed '%s'" % filename)





        # for each episode:
        #   extract .wav audio
        #   extract audience recording
        #   if audience recording is valid:
        #       extract laughter times
        #       download subtitles
        #           while subtitles don't match
        #               try another subtitle file (max retries: 4)
        #           if not found: quit
        #       download screenplay
        #       parse screenplay
        #       merge laughter_times, screenplay, subtitles


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A script to create the Seinfeld corpus from scratch.")
    parser.add_argument('episodes_path', help='A folder that contains all of the Seinfeld episodes in .mkv format.')
    args = parser.parse_args()
    episodes_path = args.episodes_path

    if not os.path.exists(episodes_path):
        print("'%s' illegal path!\n" % output)
    else:
        run(episodes_path)
