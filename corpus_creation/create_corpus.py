"""
A module that creates the annotated Seinfeld corpus from scratch, given the episodes in .mkv format.
"""

import argparse
import os
import subprocess
import ntpath


def run(episodes_path, output_path):
    for dirpath, _, filenames in os.walk(episodes_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            processor =Processor(file_path, output_path)
            processor.process()


class Processor:
    """
    A class that generates corpus data from a Seinfeld episode in the .mkv file format.
    """
    def __init__(self, filepath, outputpath):
        self.filepath = filepath      # path of the video file of the episode
        self.outputpath = outputpath  # path of the folder in which to write the output
        self.files = {}               # paths of all the temporary files that will be used in the processing

    def process(self):
        filename = ntpath.basename(self.filepath)
        try:
            print("Processing '%s'..." % filename)
            self._extract_audio()
            self._extract_laughter_times()
            self.files['laughter_times'] = self._extract_laughter_times(audio_filepath)
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
        for filename in self.files.values():
            os.remove(filename)
            print("Removed '%s'" % filename)

    def _extract_audio(self):
        # audio file name is the same as the video's but with .wav extension
        self.files['audio'] = self.filepath.rsplit(".", 1)[0] + '.wav'
        # ffmpeg will extract the audio in uncompressed PCM format.
        try:
            result = subprocess.call(["external_tools/ffmpeg/bin/ffmpeg.exe", "-i", self.filepath, self.files['audio']])
        except Exception as e:
            raise Exception("Please make sure you have a working version of ffmpeg in the external_tools folder.\n%s" % str(e))

        # you need to have ffmpeg in 'external_tools' folder. Please download it from ffmpeg.org and try again.







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


class AudienceRecordingNotInStereoException(Exception):
    pass


class SubtitlesNotInSyncException(Exception):
    pass


class ScreenplayParseException(Exception):
    pass


class MergeException(Exception):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A script to create the Seinfeld corpus from scratch.")
    parser.add_argument('episodes_path', help='A folder that contains all of the Seinfeld episodes in .mkv format.')
    parser.add_argument('output_path', help='Output will be written to this path.')
    args = parser.parse_args()
    episodes_path = args.episodes_path
    output_path = args.output_path

    if not os.path.exists(episodes_path):
        print("'%s' illegal path!\n" % episodes_path)
    elif not os.path.isdir(output_path):
        print("'%s' is not a directory!" % output_path)
    else:
        run(episodes_path, output_path)
